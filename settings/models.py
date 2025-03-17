from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from membership.models import Member  # Ensure Member model exists

class MemberSettings(models.Model):
    """
    Stores settings for each church member's dashboard.
    """
    member = models.OneToOneField(
        Member, on_delete=models.CASCADE, related_name="dashboard_settings"
    )

    # Theme Preferences
    THEME_CHOICES = [
        ("light", "Light"),
        ("dark", "Dark"),
        ("auto", "Auto (System Default)"),
    ]
    theme = models.CharField(
        max_length=10, choices=THEME_CHOICES, default="light", help_text="Dashboard theme preference."
    )

    # Notification Preferences
    receive_announcements = models.BooleanField(default=True, help_text="Receive church announcements?")
    receive_notifications = models.BooleanField(default=True, help_text="Receive church notifications?")
    receive_newsletters = models.BooleanField(default=True, help_text="Receive newsletters?")
    receive_event_reminders = models.BooleanField(default=True, help_text="Receive event reminders?")
    receive_meeting_reminders = models.BooleanField(default=True, help_text="Receive reminders for church meetings?")
    
    # Dashboard Layout Preferences
    show_recent_activities = models.BooleanField(default=True, help_text="Show recent activities on dashboard?")
    show_service_attendance = models.BooleanField(default=True, help_text="Show personal service attendance stats?")
    show_family_section = models.BooleanField(default=True, help_text="Show family section in dashboard?")

    # Privacy Settings
    profile_visibility = models.BooleanField(
        default=True, help_text="Make profile visible to other church members?"
    )

    # Language Preferences
    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("fr", "French"),
        ("es", "Spanish"),
    ]
    language_preference = models.CharField(
        max_length=5, choices=LANGUAGE_CHOICES, default="en",
        help_text="Preferred language for the dashboard."
    )

    # Security Settings
    enable_2fa = models.BooleanField(default=False, help_text="Enable two-factor authentication for login security?")

    # Auto Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Memeber Settings"

    def __str__(self):
        return f"{self.member.user.get_full_name()}'s Settings"

