from django.contrib import admin
from .models import MemberSettings

@admin.register(MemberSettings)
class MemberSettingsAdmin(admin.ModelAdmin):
    """
    Admin configuration for MemberSettings model.
    """

    # Display these fields in the list view
    list_display = (
        "member_name", "theme", "language_preference", "enable_2fa", 
        "receive_notifications", "receive_event_reminders", "updated_at"
    )

    # Enable search by member username and email
    search_fields = ("member__user__username", "member__user__email")

    # Filter by theme, language, and security settings
    list_filter = ("theme", "language_preference", "enable_2fa", "profile_visibility")

    # Read-only fields (cannot be edited)
    readonly_fields = ("created_at", "updated_at")

    # Organizing fields into sections
    fieldsets = (
        ("Member Information", {
            "fields": ("member",)
        }),
        ("Dashboard Preferences", {
            "fields": ("theme", "language_preference")
        }),
        ("Notifications", {
            "fields": (
                "receive_announcements", "receive_notifications", "receive_newsletters", 
                "receive_event_reminders", "receive_meeting_reminders"
            )
        }),
        ("Dashboard Layout", {
            "fields": ("show_recent_activities", "show_service_attendance", "show_family_section")
        }),
        ("Privacy Settings", {
            "fields": ("profile_visibility",)
        }),
        ("Security", {
            "fields": ("enable_2fa",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )

    # Custom method to display the member's full name
    def member_name(self, obj):
        return obj.member.user.get_full_name()
    member_name.short_description = "Member Name"

