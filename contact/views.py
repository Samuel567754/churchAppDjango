from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib import messages
from .forms import ContactForm
from django.shortcuts import render, redirect
from django.conf import settings
from django.utils.html import strip_tags
from django.contrib.auth.decorators import login_required
from .models import NewsletterSubscription, Newsletter, Contact, Notification
from datetime import datetime
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from membership.models import Member
from django.db.models import Q



def subscribe_newsletter(request):
    """Handles newsletter subscription"""

    # Allow GET requests to subscribe using the email from URL params
    email = request.GET.get("email") if request.method == "GET" else request.POST.get("email")

    if not email:
        messages.error(request, "Invalid request. No email provided!")
        return redirect('community:home')

    if NewsletterSubscription.objects.filter(email=email).exists():
        messages.warning(request, "You are already subscribed!")
        return redirect('community:home')  # Redirect to home or any desired page

    # Save Subscription
    NewsletterSubscription.objects.create(email=email)

    # Generate Unsubscribe URL dynamically using reverse()
    unsubscribe_url = request.build_absolute_uri(reverse('contact:unsubscribe_newsletter')) + f"?email={email}"
    print("Unsubscribe URL:", unsubscribe_url)  # Debugging output

    # Render the email as HTML
    html_content = render_to_string("contact/emails/newsletter_subscribe.html", {
        "email": email,
        "unsubscribe_url": unsubscribe_url,
        "year": datetime.now().year
    })
    plain_message = strip_tags(html_content)  # Strip HTML tags for plain text version

    # Create Email Message
    email_message = EmailMultiAlternatives(
        'Newsletter Subscription Confirmation',
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [email]
    )
    email_message.attach_alternative(html_content, "text/html")  # Attach HTML version

    # Send Email
    email_message.send(fail_silently=False)

    messages.success(request, "Subscription successful! Please check your email.")
    return redirect('community:home')  # Redirect to home or any desired page





def unsubscribe_newsletter(request):
    """Handles unsubscription"""

    # Allow GET requests to unsubscribe using the email from URL params
    email = request.GET.get("email") if request.method == "GET" else request.POST.get("email")

    if not email:
        messages.error(request, "Invalid request. No email provided!")
        return redirect('community:home')

    if NewsletterSubscription.objects.filter(email=email).exists():
        # Unsubscribe the user
        NewsletterSubscription.objects.filter(email=email).delete()

        # Generate Resubscribe URL dynamically using reverse()
        resubscribe_url = request.build_absolute_uri(reverse('contact:subscribe_newsletter')) + f"?email={email}"

        # Render the email as HTML
        html_content = render_to_string("contact/emails/newsletter_unsubscribe.html", {
            "email": email,
            "resubscribe_url": resubscribe_url,
            "year": datetime.now().year
        })
        plain_message = strip_tags(html_content)

        # Create Email Message
        email_message = EmailMultiAlternatives(
            'Newsletter Unsubscription Confirmation',
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [email]
        )
        email_message.attach_alternative(html_content, "text/html")
        email_message.send(fail_silently=False)

        messages.success(request, "Unsubscribed successfully!")
        return redirect('community:home')

    messages.error(request, "Email not found!")
    return redirect('community:home')




def send_newsletter(request, newsletter_id):
    """Sends a newsletter to all subscribers (Admin Only)"""
    try:
        newsletter = Newsletter.objects.get(id=newsletter_id, is_sent=False)
        recipients = list(NewsletterSubscription.objects.values_list('email', flat=True))

        if not recipients:
            return JsonResponse({"message": "No subscribers found!"}, status=400)

        # Prepare Email
        subject = newsletter.title
        html_message = render_to_string("contact/emails/newsletter_template.html", {
            "newsletter": newsletter,
            "year": datetime.now().year
        })
        plain_message = strip_tags(html_message)
        email_message = EmailMultiAlternatives(subject, plain_message, settings.DEFAULT_FROM_EMAIL, recipients)
        email_message.attach_alternative(html_message, "text/html")

        # Attach File (if exists)
        if newsletter.attachment:
            email_message.attach_file(newsletter.attachment.path)

        # Send Email
        email_message.send()

        # Update Newsletter Status
        newsletter.is_sent = True
        newsletter.save()

        return JsonResponse({"message": "Newsletter sent successfully!"}, status=200)

    except Newsletter.DoesNotExist:
        return JsonResponse({"message": "Newsletter not found!"}, status=404)



def contact(request):
    # Handle GET request: Render the form
    if request.method == 'GET':
        form = ContactForm()
        return render(request, 'contact/contact.html', {'form': form})

    # Handle POST request: Process the form submission
    elif request.method == 'POST':
        form = ContactForm(request.POST)

        # Check if the form is valid
        if form.is_valid():
            # Extract cleaned data from form
            name = form.cleaned_data.get('name')
            email = form.cleaned_data.get('email')
            phone = form.cleaned_data.get('phone')
            subject = form.cleaned_data.get('subject')
            message = form.cleaned_data.get('message')

            # Prepare email content for admin notification
            email_content = render_to_string('contact/emails/email_template.html', {
                'name': name,
                'email': email,
                'phone': phone,
                'subject': subject,
                'message': message,
            })

            # Send email to admin
            try:
                admin_email = EmailMessage(
                    subject=f"New Contact Message: {subject}",
                    body=email_content,
                    from_email='samytest777@gmail.com',  # Replace with your email
                    to=['samytest777@gmail.com'],  # Replace with actual admin email
                )
                admin_email.content_subtype = 'html'
                admin_email.send(fail_silently=False)

                # Send auto-response to the user
                auto_response_content = render_to_string('contact/emails/auto_response_template.html', {
                    'name': name,
                    'message': message,
                })
                auto_response_email = EmailMessage(
                    subject="Thank you for reaching out!",
                    body=auto_response_content,
                    from_email='your_email@example.com',
                    to=[email],
                )
                auto_response_email.content_subtype = 'html'
                auto_response_email.send(fail_silently=False)

                # Save the contact form to the database
                form.save()

                # Success response
                messages.success(request, 'Your message has been sent successfully.')
                return redirect('contact:contact')  # Redirect to the same page or another page

            except Exception as e:
                # Handle errors and send failure response
                messages.error(request, f"An error occurred: {str(e)}")
                return redirect('contact:contact')  # Redirect back to the contact page after error

        else:
            # Collect form errors and send failure response
            messages.error(request, 'Please fix the errors below.')
            return render(request, 'contact/contact.html', {'form': form})
        
        
# @login_required
# def member_dashboard_notifications(request):
#     """
#     Loads the member notification page (partial)
#     """
#     member = get_object_or_404(Member, user=request.user)
#     notifications = Notification.objects.filter(member=member).order_by('-created_at')
#     context = {
#         'member': member,
#         'notifications': notifications
#     }
#     return render(request, 'contact/member_dashboard_notifications.html', context)


# @login_required
# def notification_detail(request, notification_id):
#     """ View a specific notification and mark it as read """
#     notification = get_object_or_404(Notification, id=notification_id, member=request.user.member)
    
#     if not notification.is_read:
#         notification.is_read = True
#         notification.save()
#         messages.success(request, "Notification marked as read.")

#     return redirect('contact:member_dashboard_notifications')

# @login_required
# def mark_all_read(request):
#     """ Mark all notifications as read """
#     member = request.user.member
#     unread_notifications = Notification.objects.filter(member=member, is_read=False)

#     if unread_notifications.exists():
#         unread_notifications.update(is_read=True)
#         messages.success(request, "All notifications marked as read.")
#     else:
#         messages.info(request, "No unread notifications to mark.")

#     return redirect('contact:member_dashboard_notifications')


# @login_required
# def mark_as_read(request, notification_id):
#     """ Mark a specific notification as read """
#     notification = get_object_or_404(Notification, id=notification_id, member=request.user.member)

#     if not notification.is_read:
#         notification.is_read = True
#         notification.save()
#         messages.success(request, "Notification marked as read.")

#     return redirect('contact:member_dashboard_notifications')  # Change this to your actual notification list view name

# @login_required
# def notification_delete(request, pk):
#     """
#     Deletes a specific notification.
#     """
#     notification = get_object_or_404(Notification, pk=pk, member__user=request.user)

#     if request.method == "POST":
#         notification.delete()
#         messages.success(request, "Notification deleted successfully.")
#         return redirect('contact:member_dashboard_notifications')

#     messages.error(request, "Invalid request method")
#     return redirect('contact:member_dashboard_notifications')


@login_required
def member_dashboard_notifications(request):
    """Loads notifications relevant to the member (both general and member-specific)."""
    member = getattr(request.user, 'member', None)
    
    # If the user has a member profile, show both general and member-specific notifications.
    # Otherwise, show only general notifications.
    if member:
        notifications = Notification.objects.filter(
            Q(member__isnull=True) | Q(member=member)
        ).order_by('-created_at')
    else:
        notifications = Notification.objects.filter(
            member__isnull=True
        ).order_by('-created_at')

    context = {
        'member': member,
        'notifications': notifications
    }
    return render(request, 'contact/member_dashboard_notifications.html', context)



@login_required
def notification_detail(request, notification_id):
    """ View a specific notification and mark it as read. """
    notification = get_object_or_404(
        Notification,
        Q(member__isnull=True) | Q(member=request.user.member),  # Allow both general & member-specific
        id=notification_id
    )
    
    if not notification.is_read:
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        messages.success(request, "Notification marked as read.")

    return redirect('contact:member_dashboard_notifications')

@login_required
def mark_all_read(request):
    """ Mark all general and member-specific notifications as read. """
    member = getattr(request.user, 'member', None)

    # Update both general and member-specific notifications
    unread_count = Notification.objects.filter(
        Q(member__isnull=True) | Q(member=member),
        is_read=False
    ).update(is_read=True)

    if unread_count > 0:
        messages.success(request, f"Marked {unread_count} notifications as read.")
    else:
        messages.info(request, "No unread notifications to mark.")

    return redirect('contact:member_dashboard_notifications')

@login_required
def mark_as_read(request, notification_id):
    """ Mark a specific notification as read. """
    notification = get_object_or_404(
        Notification,
        Q(member__isnull=True) | Q(member=request.user.member),
        id=notification_id
    )

    if not notification.is_read:
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        messages.success(request, "Notification marked as read.")

    return redirect('contact:member_dashboard_notifications')

@login_required
def notification_delete(request, pk):
    """ Deletes a specific notification if the request is a POST request. """
    notification = get_object_or_404(
        Notification,
        Q(member__isnull=True) | Q(member=request.user.member),
        pk=pk
    )

    if request.method == "POST":
        notification.delete()
        messages.success(request, "Notification deleted successfully.")
    else:
        messages.error(request, "Invalid request method.")

    return redirect('contact:member_dashboard_notifications')