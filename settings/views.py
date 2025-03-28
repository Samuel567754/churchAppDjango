from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from membership.models import Member, Membership, Family, Attendance, Ministry
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
from .forms import MemberSettingsForm
from .models import MemberSettings
from django.utils.decorators import method_decorator
from django.views import View

# @method_decorator(login_required, name="dispatch")
# class MemberSettingsView(View):
#     """
#     View to handle church members' settings.
#     """
#     template_name = "settings/member_settings.html"

#     def get(self, request):
#         member_settings, created = MemberSettings.objects.get_or_create(member=request.user.member)
#         form = MemberSettingsForm(instance=member_settings)
#         return render(request, self.template_name, {"form": form})

#     def post(self, request):
#         member_settings, created = MemberSettings.objects.get_or_create(member=request.user.member)
#         form = MemberSettingsForm(request.POST, instance=member_settings)

#         if form.is_valid():
#             form.save()
#             messages.success(request, "Your settings have been updated successfully.")
#             return redirect("settings:member-settings")
#         else:
#             messages.error(request, "Please correct the errors below.")

#         return render(request, self.template_name, {"form": form})




@method_decorator(login_required, name="dispatch")
class MemberSettingsView(View):
    template_name = "settings/member_settings.html"
    form_template_name = "settings/partials/_member_settings_form.html"

    def get(self, request):
        member_settings, created = MemberSettings.objects.get_or_create(member=request.user.member)
        form = MemberSettingsForm(instance=member_settings)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        member_settings, created = MemberSettings.objects.get_or_create(member=request.user.member)
        form = MemberSettingsForm(request.POST, instance=member_settings)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if form.is_valid():
            form.save()
            
            # Create a notification for the successful update of settings.
            Notification.objects.create(
                title="Settings Updated",
                content="Your member settings have been updated successfully.",
                member=request.user.member
            )

            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Settings saved successfully.'
                })
            messages.success(request, "Your settings have been updated successfully.")
            return redirect("settings:member-settings")
        else:
            if is_ajax:
                form_html = render_to_string(self.form_template_name, {"form": form}, request=request)
                return JsonResponse({'success': False, 'form_html': form_html})
            messages.error(request, "Please correct the errors below.")
            return render(request, self.template_name, {"form": form})