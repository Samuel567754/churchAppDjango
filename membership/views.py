from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from .models import Member, Membership, Family, Attendance, Ministry
from account.models import Church
from contact.models import Staff, Notification
from event.models import Event, EventRegistration
from finance.models import Donation
from account.models import Church
from worship.models import PrayerRequest, Appointment
from community.models import Announcement, VolunteerApplication, VolunteerOpportunity, Survey, SurveyResponse, Poll, PollOption, PollVote, Testimonial
from django.utils import timezone
from django.contrib import messages
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
from .forms import FamilyForm, FamilyMemberForm


@login_required
def member_dashboard_ministries(request):
    """
    Loads the ministries page for the member dashboard (partial)
    """
    member = get_object_or_404(Member, user=request.user)
    all_ministries = member.ministries.all()  # Ensure 'ministries' is a related_name in the model
    context = {
        'member': member,
        'all_ministries': all_ministries
    }
    return render(request, 'membership/member_dashboard_ministries.html', context)

def ministry_detail(request, slug):
    # Fetch the ministry or return a 404 error if not found
    ministry = get_object_or_404(Ministry, slug=slug)
    
    # Handle image URL logic
    if ministry.image:
        image_url = ministry.image.url  # Get the image URL from the 'image' field
        print('image is not in ministry.image')
    elif ministry.image_url:
        image_url = ministry.image_url  # Use the external URL if available
        print('image is in ministry.image_url')
    else:
        image_url = None  # Set to None if no image exists
        print('there is no image to display')
    
    # Prepare the response data
    data = {
        'name': ministry.name,
        'description': ministry.description,
        'leader': ministry.leader.user.get_full_name() if ministry.leader else "Not assigned",
        'members': [member.user.get_full_name() for member in ministry.members.all()],
        'image_url': image_url,  # Pass the image URL (either from 'image' or 'image_url')
    }

    # Return a JSON response with the data
    return JsonResponse(data)


def all_ministries(request):
    """
    Loads the ministries page for the member dashboard (partial).
    Retrieves all Ministry instances from the database.
    """
    # Use the default model manager to get all Ministry instances.
    ministries = Ministry.objects.all()
    
    context = {
        'ministries': ministries,
    }
    
    return render(request,'membership/all_ministries.html', context)


# @login_required
# def member_dashboard(request):
#     """
#     Base Member dashboard, loads the base template with the menu
#     """      
#     return render(request, 'membership/member_dashboard.html',)


@login_required
def member_dashboard_home(request):
    """
    Loads the member dashboard home page (partial)
    """
    member = get_object_or_404(Member, user=request.user)
    announcements = Announcement.objects.filter(status='published').order_by('-date_posted')[:5]
    events = Event.objects.filter(date__gte=timezone.now()).order_by('date')[:5]
    surveys = Survey.objects.all()[:3]
    polls = Poll.objects.filter(is_active=True)[:3]
    
    context = {
        'member': member,
        'announcements': announcements,
        'events': events,
        'surveys': surveys,
        'polls': polls,
    }
    return render(request, 'membership/member_dashboard_home.html', context)

@login_required
def member_dashboard_announcements(request):
    """
    Display a list of announcements
    """
    announcements = Announcement.objects.filter(status='published').order_by('-date_posted')
    return render(request, 'membership/annousment_list.html', {'announcements': announcements})

@login_required
def announcement_detail(request, announcement_id):
    """
    Display the details of a single announcement.
    Only shows published announcements.
    """
    announcement = get_object_or_404(Announcement, id=announcement_id, status='published')

    return render(request, 'membership/announcement_detail.html', {'announcement': announcement})

@login_required
def member_dashboard_attendance(request):
    """
    Loads the attendance page of the member dashboard (partial)
    """
    member = get_object_or_404(Member, user=request.user)
    attendances = Attendance.objects.filter(member=member).order_by('-date')
    context = {
        'member': member,
        'attendances': attendances
    }
    return render(request, 'membership/member_dashboard_attendance.html', context)


@login_required
def member_dashboard_donations(request):
    """
    Loads the donation page of the member dashboard (partial)
    """
    member = get_object_or_404(Member, user=request.user)
    donations = Donation.objects.filter(donor=request.user).order_by('-date')
    context = {
        'member': member,
        'donations': donations
    }
    return render(request, 'membership/member_dashboard_donations.html', context)



@login_required
def member_dashboard_events(request):
    """
    Loads the events page of the member dashboard (partial)
    """
    member = get_object_or_404(Member, user=request.user)
    registrations = EventRegistration.objects.filter(member=member).order_by('-registration_date')
    context = {
        'member': member,
        'registrations': registrations
    }
    return render(request, 'membership/member_dashboard_events.html', context)


@login_required
def member_dashboard_volunteer(request):
    """
    Loads the volunteer application page for the member (partial)
    """
    member = get_object_or_404(Member, user=request.user)
    applications = VolunteerApplication.objects.filter(member=member).order_by('-application_date')
    opportunities = VolunteerOpportunity.objects.filter(is_active=True)
    context = {
      'member': member,
      'applications': applications,
      'opportunities': opportunities
    }
    return render(request, 'membership/member_dashboard_volunteer.html', context)

@login_required
def apply_for_volunteer_opportunity(request, opportunity_id):
    """
    Handles volunteer application submission
    """
    member = get_object_or_404(Member, user=request.user)
    opportunity = get_object_or_404(VolunteerOpportunity, id=opportunity_id)

    if request.method == 'POST':
        notes = request.POST.get('notes', '')

        # Check if a similar application exists
        if not VolunteerApplication.objects.filter(member=member, opportunity=opportunity).exists():
            VolunteerApplication.objects.create(member=member, opportunity=opportunity, notes=notes)
        
        return JsonResponse({'status': 'success', 'message': 'Application submitted.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)


@login_required
def withdraw_from_volunteer_opportunity(request, application_id):
    application = get_object_or_404(VolunteerApplication, id=application_id, member__user=request.user)
    application.delete()
    return JsonResponse({'status': 'success', 'message': 'Application withdrawn.'})




@login_required
def add_family_member(request, pk):
    family = get_object_or_404(Family, pk=pk)
    
    # Restrict access: Only a member of the family can add new members.
    if request.user.member not in family.members.all():
        messages.error(request, "You are not allowed to add members to this family.")
        return redirect('membership:family_detail', pk=family.pk)
    
    # Build a queryset excluding members already in the family.
    queryset = Member.objects.exclude(pk__in=family.members.values_list('pk', flat=True))
    
    if request.method == "POST":
        form = FamilyMemberForm(request.POST)
        form.fields['member'].queryset = queryset
        if form.is_valid():
            member = form.cleaned_data['member']
            family.members.add(member)
            
            # Create a notification for the newly added member.
            Notification.objects.create(
                title="Added to Family",
                content=f"You have been added to the family: {family.name}" if hasattr(family, 'name') else "You have been added to a family.",
                member=member
            )
            
            messages.success(request, f"{member.user.get_full_name()} has been added to the family.")
            return redirect('membership:member_family')
        else:
            messages.error(request, "There was an error adding the member. Please try again.")
    else:
        form = FamilyMemberForm()
        form.fields['member'].queryset = queryset

    return render(request, 'membership/add_family_member.html', {'form': form, 'family': family})






@login_required
def member_family(request):
    # Get the member object associated with the logged-in user.
    member = request.user.member
    
    # Retrieve all families that this member is part of, along with their related members.
    families = member.family_members.prefetch_related('members')
    
    # Pass the member and families to the template.
    context = {
        "member": member,
        "families": families,
    }
    
    return render(request, "membership/member_family.html", context)

@login_required
def list_families(request):
    families = Family.objects.all()
    return render(request, 'membership/family_list.html', {'families': families})


@login_required
def create_family(request):
    member = request.user.member  # Get the logged-in member
    
    # Count the number of families the member is part of using the reverse relation 'family_members'
    current_family_count = member.family_members.count()
    
    # If the member is already part of two families, they cannot create another
    if current_family_count >= 2:
        messages.error(request, "You are already part of two families. You cannot create a new family.")
        return redirect('membership:member_family')
    
    if request.method == "POST":
        form = FamilyForm(request.POST)
        if form.is_valid():
            family = form.save(commit=False)
            # Set the current member as the head_of_family (creator)
            family.head_of_family = member
            family.save()
            # Add the creator as a family member.
            family.members.add(member)

            # Create a notification for the successful creation of a family
            Notification.objects.create(
                title="Family Created",
                content="Your family has been created successfully.",
                member=member
            )

            messages.success(request, "Family created successfully.")
            return redirect('membership:member_family')
        else:
            messages.error(request, "There was an error creating the family. Please correct the errors below.")
    else:
        # Set the current member as the default head_of_family
        form = FamilyForm(initial={'head_of_family': member.pk})
    
    return render(request, 'membership/create_family.html', {'form': form})



@login_required
def edit_family(request, pk):
    family = get_object_or_404(Family, pk=pk)
    
    # Restrict access: Only a member of the family can edit its details.
    if request.user.member not in family.members.all():
        messages.error(request, "You are not allowed to edit this family.")
        return redirect('membership:family_detail', pk=family.pk)
    
    # Store the current head to compare later.
    old_head = family.head_of_family

    if request.method == "POST":
        form = FamilyForm(request.POST, instance=family)
        # Remove head_of_family field if current user is not the head.
        if request.user.member != old_head:
            form.fields.pop('head_of_family', None)
        if form.is_valid():
            updated_family = form.save(commit=False)
            # Ensure non-head members cannot change the head.
            if request.user.member != old_head:
                updated_family.head_of_family = old_head
            updated_family.save()
            
            # Create a notification for the logged-in member about the update
            Notification.objects.create(
                title="Family Details Updated",
                content="Your family details have been updated successfully.",
                member=request.user.member
            )
            
            # Notify if the head has changed (only applicable when the head is editing)
            if request.user.member == old_head:
                new_head = updated_family.head_of_family
                if new_head != old_head:
                    messages.success(
                        request, 
                        f"Family details updated successfully. New head of family is {new_head.user.get_full_name()}."
                    )
                    # Create a notification for the new head of family
                    Notification.objects.create(
                        title="New Head Assigned",
                        content="You have been assigned as the new head of the family.",
                        member=new_head
                    )
                else:
                    messages.success(request, "Family details updated successfully.")
            else:
                messages.success(request, "Family details updated successfully.")
            return redirect('membership:member_family')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = FamilyForm(instance=family)
        # Remove the head_of_family field if current user is not the head.
        if request.user.member != old_head:
            form.fields.pop('head_of_family', None)
    
    # Get the current family members to list them for possible removal.
    family_members = family.members.all()
    
    context = {
        'form': form,
        'family': family,
        'family_members': family_members,
    }
    
    return render(request, 'membership/edit_family.html', context)

# @login_required
# def family_detail(request, pk):
#     family = get_object_or_404(Family, pk=pk)
#     return render(request, 'membership/family_detail.html', {'family': family})


@login_required
def family_detail(request, pk):
    # Fetch the family object
    family = get_object_or_404(Family, pk=pk)
    
    # Prepare family data
    family_data = {
        'family_name': family.family_name,
        'address': family.address,
        'phone_number': family.phone_number,
        'head_of_family': family.head_of_family.user.get_full_name() if family.head_of_family else None,
        'members_count': family.get_family_size(),
        'members': [
            {
                'name': member.user.get_full_name() or member.user.username,
                'phone': member.phone,
                'address': member.address,
                'email': member.user.email,
                'date_of_birth': member.date_of_birth.strftime('%Y-%m-%d') if member.date_of_birth else None,
                'date_joined': member.date_joined.strftime('%Y-%m-%d'),
                'baptized': member.baptized,
                'role': 'Head' if member == family.head_of_family else 'Member'
            }
            for member in family.get_family_members()
        ]
    }
    
    return JsonResponse(family_data)




@login_required
def remove_family_member(request, family_id, member_id):
    family = get_object_or_404(Family, pk=family_id)
    member_to_remove = get_object_or_404(Member, pk=member_id)
    
    # Ensure the logged-in user is part of the family.
    if request.user.member not in family.members.all():
        messages.error(request, "You are not allowed to modify this family.")
        return redirect('membership:edit_family', pk=family.pk)
    
    # Check if the member to remove is the family head.
    if member_to_remove == family.head_of_family:
        # Only allow the head to remove themselves.
        if request.user.member != family.head_of_family:
            messages.error(request, "The family head cannot be removed by any member.")
            return redirect('membership:edit_family', pk=family.pk)
        else:
            # The head is removing themselves, so delete the entire family.
            family.delete()
            # Create a notification for the head about the deletion.
            Notification.objects.create(
                title="Family Deleted",
                content=f"You removed yourself as the family head of {family.family_name}. The family has been deleted.",
                member=request.user.member
            )
            messages.success(request, "You removed yourself as the family head. The family has been deleted.")
            return redirect('membership:member_family')
    else:
        # For any other member, simply remove them from the family.
        if member_to_remove in family.members.all():
            family.members.remove(member_to_remove)
            # Create a notification for the removed member.
            Notification.objects.create(
                title="Removed from Family",
                content=f"You have been removed from the family: {family.family_name}.",
                member=member_to_remove,
            )
            messages.success(request, f"{member_to_remove.user.get_full_name()} has been removed from the family.")
            return redirect('membership:edit_family', pk=family.pk)
        else:
            messages.error(request, "Member not found in the family.")
        return redirect('membership:edit_family', pk=family.pk)




@login_required
def delete_family(request, pk):
    family = get_object_or_404(Family, pk=pk)
    
    # Only allow deletion if the current user is the family creator (head_of_family).
    if request.user.member != family.head_of_family:
        messages.error(request, "You are not authorized to delete this family.")
        return redirect('membership:family_detail', pk=family.pk)
    
    if request.method == "GET":
        family.delete()
        
        # Create a notification to inform the head that their family has been deleted.
        Notification.objects.create(
            title=f"Family Deleted: {family.family_name}.",
            content=f"Your family {family.family_name}, has been deleted successfully.",
            member=request.user.member
        )
        
        messages.success(request, "Family deleted successfully.")
        return redirect('membership:member_family')
    else:
        messages.error(request, "Invalid request method for deleting family.")
        return redirect('membership:member_family')




