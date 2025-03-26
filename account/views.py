from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from membership.models import Member, Membership, Family, Attendance, Ministry
from .models import Church
from django.utils import timezone
from django.contrib import messages
from .forms import UserRegistrationForm, MemberProfileForm, UserProfileForm, MemberLoginForm
from django.db.models import Q
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags  # Import strip_tags
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from django.utils.http import url_has_allowed_host_and_scheme
from urllib.parse import urlparse
from contact.models import Notification
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from account.utils import generate_action_link



# views.py
from django.contrib.auth import get_user_model

def check_username(request):
    username = request.GET.get('username', '')
    User = get_user_model()
    
    if len(username) < 4:
        return JsonResponse({'available': False, 'message': 'Username too short'})
    
    exists = User.objects.filter(username__iexact=username).exists()
    return JsonResponse({
        'available': not exists,
        'message': 'Username available' if not exists else 'Username already taken'
    })


# def member_action(request, token):
#     signer = TimestampSigner()
#     try:
#         # Unsigned token should be in the format "member_id:action"
#         unsigned = signer.unsign(token, max_age=86400)  # token valid for 24 hours
#         member_pk, action = unsigned.split(':')
#     except (BadSignature, SignatureExpired):
#         return HttpResponse("Invalid or expired link.", status=400)

#     member = get_object_or_404(Member, pk=member_pk)
#     if action == 'approve':
#         member.approval_status = 'approved'
#         message = "Member approved."
#     elif action == 'reject':
#         member.approval_status = 'rejected'
#         message = "Member rejected."
#     else:
#         return HttpResponse("Invalid action.", status=400)
    
#     member.save()
#     return HttpResponse(message)

def member_action(request, token):
    signer = TimestampSigner()
    try:
        # Token is expected in the format "member_id:action"
        unsigned = signer.unsign(token, max_age=86400)  # Token valid for 24 hours
        member_pk, action = unsigned.split(':')
    except (BadSignature, SignatureExpired):
        messages.error(request, "Invalid or expired link.")
        return redirect('admin:index')  # Replace with your desired URL name

    member = get_object_or_404(Member, pk=member_pk)
    
    if action == 'approve':
        member.approval_status = 'approved'
        messages.success(request, "Member approved successfully.")
    elif action == 'reject':
        member.approval_status = 'rejected'
        messages.success(request, "Member rejected successfully.")
    else:
        messages.error(request, "Invalid action specified.")
        return redirect('admin:index')  # Replace with your desired URL name

    member.save()
    return redirect('admin:index')  # Replace with your desired URL name



@login_required
def member_dashboard_profile(request):
    """
    Loads the profile page for the member dashboard (partial)
    """
    member = get_object_or_404(Member, user=request.user)
    family_members = None
    if member.family_members.exists():
        family = member.family_members.first()
        family_members = family.members.all()

    context = {
        'member': member,
        'family_members': family_members
    }
    return render(request, 'account/member_dashboard_profile.html', context)


def member_register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        member_form = MemberProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and member_form.is_valid():
            # Create the User object
            user = user_form.save(commit=False)  # Don't save yet
            user.set_password(user.password)  # Hash the password
            user.save()  # Now save with hashed password

            # Create the Member object
            member = member_form.save(commit=False)  # Don't save yet
            member.user = user  # Link the member to the user
            member.approval_status = 'pending'  # Set approval status
            member.save()  # Save member first

            member_form.save_m2m()  # ✅ Save ManyToMany fields like ministries

            # Send emails
            send_email_pending_approval(user)
            send_admin_new_registration_email(request, user, member)

            messages.success(request, 'Registration successful! Your account is awaiting approval from an admin.')
            return redirect('account:login')  # Redirect to login page

    else:
        user_form = UserRegistrationForm()
        member_form = MemberProfileForm()

    return render(request, 'account/register.html', {'user_form': user_form, 'member_form': member_form})




def send_email_pending_approval(user):
    subject = 'Your Membership Application is Pending Approval'
    from_email = settings.DEFAULT_FROM_EMAIL  # Ensure you have this in settings.py
    
    context = {
        'user': user,
        'domain': settings.SITE_DOMAIN,
        'local': settings.LOCAL_DOMAIN,
    }
    
    # Render the email as HTML
    html_content = render_to_string('account/emails/member_pending_approval_email.html', context) 

    # Create email message
    email = EmailMultiAlternatives(subject, strip_tags(html_content), from_email, [user.email])
    email.attach_alternative(html_content, "text/html")  # Attach HTML version

    email.send(fail_silently=False)

def send_admin_new_registration_email(request, user, member):
    subject = 'New Member Registration'
    from_email = settings.DEFAULT_FROM_EMAIL  # Ensure this is defined in your settings.py

    # Generate secure action links for approving and rejecting the member
    approve_link = generate_action_link(request, member, 'approve')
    reject_link = generate_action_link(request, member, 'reject')

    # Render the email as HTML with the additional links
    html_content = render_to_string('account/emails/new_registration_email.html', {
        'user': user,
        'member': member,
        'approve_link': approve_link,
        'reject_link': reject_link,
    })

    # Get admin email from settings
    admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@example.com')

    # Create and send the email
    email = EmailMultiAlternatives(subject, strip_tags(html_content), from_email, [admin_email])
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)



@login_required
def edit_profile(request):
    """
    Allows members to edit their profile (both User and Member data) and creates
    a notification after a successful update.
    """
    user = request.user
    member = get_object_or_404(Member, user=user)

    if request.method == "POST":
        user_form = UserProfileForm(request.POST, instance=user)
        member_form = MemberProfileForm(request.POST, request.FILES, instance=member)
        ministries = Ministry.objects.all()  # Get all ministries
        selected_ministries = request.POST.getlist("ministries")  # Get selected ministries from form

        # Check if user requested to remove the photo
        remove_photo = request.POST.get("remove_photo") == "true"

        if user_form.is_valid() and member_form.is_valid():
            user_form.save()
            member_form.save()

            # Only update ministries if the field exists
            if hasattr(member, "ministries"):
                member.ministries.set(selected_ministries)

            if remove_photo:  # If user removed the image
                member.photo.delete(save=False)  # Delete the image from storage
                member.photo = None  # Set the field to empty
                member.save()

            # Create a notification for the member's profile update
            Notification.objects.create(
                title="Profile Updated",
                content="Your profile has been updated successfully.",
                member=member
            )

            messages.success(request, "Your profile has been updated successfully!")
            return redirect('account:member_dashboard_profile')  # Redirect to profile page

    else:
        user_form = UserProfileForm(instance=user)
        member_form = MemberProfileForm(instance=member)

    return render(request, 'account/edit_profile.html', {
        'user_form': user_form,
        'member_form': member_form,
        'ministries': Ministry.objects.all(),
    })



@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in after password change
            messages.success(request, "Your password was successfully updated!")

            # Create a notification for the successful password change
            member = get_object_or_404(Member, user=request.user)
            Notification.objects.create(
                title="Password Changed",
                content="Your password has been updated successfully.",
                member=member
            )

            return redirect('account:member_dashboard_profile')
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(user=request.user)
    
    return render(request, 'account/change_password.html', {'form': form})



# def member_login(request):
#     """Handles member login"""
#     if request.user.is_authenticated:
#         return redirect('membership:member_dashboard_home') 

#     if request.method == 'POST':
#         form = MemberLoginForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             user = authenticate(request, username=username, password=password)
            
#             if user is not None:
#                 login(request, user)

#                 # Check if the user is a registered member and if the approval status is not 'pending' or 'rejected'
#                 if hasattr(user, 'member'):
#                     member = user.member  # Get the associated member instance
#                     if member.approval_status == 'approved':
#                         # Member is approved, proceed to dashboard
#                         messages.success(request, 'Login successful! Welcome back.')
#                         return redirect('membership:member_dashboard_home')  # Redirect to member dashboard
#                     else:
#                         # Member is either pending or rejected, log them out and show an error message
#                         logout(request)
#                         if member.approval_status == 'pending':
#                             messages.error(request, 'Your membership application is pending approval. Please wait until it is reviewed.')
#                         elif member.approval_status == 'rejected':
#                             messages.error(request, 'Your membership application has been rejected. Please contact the admin for more details.')
#                         return redirect('account:login')
#                 else:
#                     # User is not a member, log them out and show an error message
#                     logout(request)
#                     messages.error(request, 'You are not registered as a church member.')
#                     return redirect('account:login')

#             else:
#                 messages.error(request, 'Invalid username or password. Please try again.')

#     else:
#         form = MemberLoginForm()

#     return render(request, 'account/login.html', {'form': form})



def member_login(request):
    """Handles member login with redirection to intended URL"""
    if request.user.is_authenticated:
        return redirect('membership:member_dashboard_home') 

    next_url = request.GET.get('next')  # Capture the intended URL from GET parameter

    if request.method == 'POST':
        form = MemberLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)

                # Check if user is a registered member and approved
                if hasattr(user, 'member'):
                    member = user.member  
                    if member.approval_status == 'approved':
                        messages.success(request, 'Login successful! Welcome back.')

                        # Retrieve next URL from POST request if available
                        next_url = request.POST.get('next') or next_url

                        # Validate next_url to prevent open redirect vulnerability
                        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                            return redirect(next_url)

                        return redirect('membership:member_dashboard_home')  # Default redirect

                    else:
                        logout(request)
                        if member.approval_status == 'pending':
                            messages.error(request, 'Your membership application is pending approval. Please wait until it is reviewed.')
                        elif member.approval_status == 'rejected':
                            messages.error(request, 'Your membership application has been rejected. Please contact the admin for more details.')
                        return redirect('account:login')

                else:
                    logout(request)
                    messages.error(request, 'You are not registered as a church member.')
                    return redirect('account:login')

            else:
                messages.error(request, 'Invalid username or password. Please try again.')

    else:
        form = MemberLoginForm()

    return render(request, 'account/login.html', {'form': form, 'next': next_url})



@login_required
def member_logout(request):
    """Handles member logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('community:home')

class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'account/registration/password_reset_confirm.html'
    success_url = reverse_lazy('account:password_reset_complete')  # Ensure correct namespace


class CustomPasswordResetView(PasswordResetView):
    template_name = 'account/registration/password_reset.html'
    email_template_name = 'account/emails/password_reset_email.html'
    subject_template_name = 'account/emails/password_reset_subject.txt'
    success_url = reverse_lazy('account:password_reset_done')  # Ensure this matches your URL
   
    
    def send_mail(self, subject, message, from_email, to_email, **kwargs):
        email = EmailMultiAlternatives(subject, message, from_email, to_email, **kwargs)
        email.attach_alternative(message, "text/html")
        email.send()

    def form_valid(self, form):
        request = self.request
        email = form.cleaned_data.get('email')

        # ✅ Check if the email exists before proceeding
        if not User.objects.filter(email=email).exists():
            form.add_error('email', _("This email address is not registered."))
            messages.error(request, _("This email address is not registered."))
            return self.form_invalid(form)  # ✅ Prevent further processing

        # ✅ Add a success message before sending the reset email
        messages.success(request, _("Password reset instructions have been sent to your email address."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below and try again."))
        return super().form_invalid(form)  
