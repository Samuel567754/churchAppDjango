from django.contrib import admin
from .models import Staff, Contact, Notification, NewsletterSubscription, Newsletter
from .views import subscribe_newsletter, unsubscribe_newsletter, send_newsletter



@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('member_name', 'position', 'is_active', 'order', 'phone', 'email')  # Ensure 'member_name' is listed here
    list_filter = ('is_active',)
    search_fields = ('member__user__username', 'position', 'bio')
    ordering = ['order']
    fieldsets = (
        ('Basic Information', {
            'fields': ('member', 'position', 'bio', 'phone', 'email', 'order', 'is_active'),
            'classes': ('extrapretty', 'wide'),
        }),
        ('Social Media Links', {
            'fields': ('facebook', 'twitter', 'instagram', 'linkedin', 'youtube'),
            'classes': ('collapse', 'extrapretty'),
        }),
        ('Image', {
            'fields': ('image',),
            'classes': ('extrapretty',),
        }),
    )

    def member_name(self, obj):
        """Returns the full name of the related user."""
        # Check if the related member and user exist
        if obj.member and obj.member.user:
            return f"{obj.member.user.first_name} {obj.member.user.last_name}"
        return "No Member"
    member_name.short_description = "Member Name"  # This sets the column header


# @admin.register(Contact)
# class ContactAdmin(admin.ModelAdmin):
#     list_display = ('name', 'subject','phone', 'email', 'date_sent')
#     list_filter = ('date_sent',)
#     search_fields = ('name', 'email', 'subject')
#     fieldsets = (
#         (None, {
#             'fields': ('name', 'email','phone','subject', 'message'),
#             'classes': ('extrapretty', 'wide'),
#         }),
#     )



@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'phone', 'email', 'status', 'responded', 'date_sent')
    list_filter = ('status', 'responded', 'date_sent')
    search_fields = ('name', 'email', 'subject', 'message')
    ordering = ('-date_sent',)
    readonly_fields = ('date_sent',)

    fieldsets = (
        ("Contact Details", {
            'fields': ('name', 'email', 'phone', 'subject', 'message'),
            'classes': ('extrapretty', 'wide'),
        }),
        ("Status", {
            'fields': ('status', 'responded'),
            'classes': ('collapse',),
        }),
    )

    actions = ['mark_as_responded', 'mark_as_pending']

    def mark_as_responded(self, request, queryset):
        queryset.update(status=Contact.StatusChoices.RESOLVED, responded=True)
        self.message_user(request, "Selected messages marked as resolved.")
    mark_as_responded.short_description = "Mark selected as Responded"

    def mark_as_pending(self, request, queryset):
        queryset.update(status=Contact.StatusChoices.PENDING, responded=False)
        self.message_user(request, "Selected messages marked as pending.")
    mark_as_pending.short_description = "Mark selected as Pending"



@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'member_name', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('title', 'member__user__username')
    ordering = ['-created_at']

    fieldsets = (
        (None, {
            'fields': ('member', 'title', 'content', 'is_read'),  
            'classes': ('extrapretty', 'wide'),
        }),
    )

    def member_name(self, obj):
        """Returns the full name of the member if available, otherwise 'General Notification'."""
        if obj.member and hasattr(obj.member, 'user'):
            return f"{obj.member.user.get_full_name() or obj.member.user.username}"
        return "General Notification"

    member_name.short_description = "Recipient"




@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    list_filter = ('subscribed_at',)
    search_fields = ('email',)
    fieldsets = (
        (None, {
            'fields': ('email',),
            'classes': ('extrapretty',),
        }),
    )


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_sent', 'is_sent')
    list_filter = ('is_sent', 'date_sent')
    search_fields = ('title', 'content')
    ordering = ['-date_sent']
    fieldsets = (
        (None, {
            "fields": ('title', 'content', 'recipients', 'attachment', 'is_sent'),
            'classes': ('extrapretty', 'wide'),
        }),
    )
    actions = ['send_selected_newsletters']
    
    def send_selected_newsletters(self, request, queryset):
        """Admin action to send selected newsletters"""
        for newsletter in queryset.filter(is_sent=False):
            send_newsletter(request, newsletter.id)  # Pass `request` correctly
        self.message_user(request, "Selected newsletters sent successfully!")

    send_selected_newsletters.short_description = "Send selected newsletters"

    


