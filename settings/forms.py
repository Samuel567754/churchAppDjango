from django import forms
from .models import MemberSettings

class MemberSettingsForm(forms.ModelForm):
    """
    Form for members to update their dashboard settings.
    """
    class Meta:
        model = MemberSettings
        fields = [
            "theme",
            "receive_announcements",
            "receive_notifications",
            "receive_newsletters",
            "receive_event_reminders",
            "receive_meeting_reminders",
            "show_recent_activities",
            "show_service_attendance",
            "show_family_section",
            "profile_visibility",
            "language_preference",
            "enable_2fa",
        ]
        widgets = {
            "theme": forms.Select(attrs={"class": "form-control"}),
            "receive_announcements": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "receive_notifications": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "receive_newsletters": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "receive_event_reminders": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "receive_meeting_reminders": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "show_recent_activities": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "show_service_attendance": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "show_family_section": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "profile_visibility": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "language_preference": forms.Select(attrs={"class": "form-control"}),
            "enable_2fa": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
