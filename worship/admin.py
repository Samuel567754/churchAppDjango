from django.contrib import admin
from .models import (
    Service,
    Sermon,
    # SermonSeries,
    SermonTag,
    ServiceSchedule,
    Appointment,
    Schedule,
    LiveStream,
    Resource,
    PrayerRequest,
    Role,
    Day,
    ServiceAttendance,
)
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from membership.models import Member  # Adjust this path based on your project structure
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from .forms import AppointmentFormSet
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.utils.text import Truncator
from django.db.models import Q
import logging
from .utils import send_email_notification  # Import the function
# from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule

logger = logging.getLogger(__name__)  # Logging setup


# admin.site.register(PeriodicTask)
# admin.site.register(IntervalSchedule)
# admin.site.register(CrontabSchedule)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'day_of_week', 'start_time', 'end_time', 'location', 'church')
    list_filter = ('day_of_week', 'church')
    search_fields = ('name', 'location', 'description')
    fieldsets = (
        (None, {
            'fields': ('name', 'church')
        }),
        ('Details', {
            'fields': ('day_of_week', 'start_time', 'end_time', 'location', 'description')
        })
    )
    ordering = ['day_of_week', 'start_time']


# @admin.register(Sermon)
# class SermonAdmin(admin.ModelAdmin):
#     list_display = ('title', 'preacher', 'date', 'is_featured', 'image_preview', 'video_url', 'audio_file', 'document')
#     list_filter = ('is_featured', 'date', 'tags', 'series')
#     search_fields = ('title', 'description', 'preacher__name')
#     filter_horizontal = ('series', 'tags')
#     prepopulated_fields = {'slug': ('title',)}
#     date_hierarchy = 'date'

#     fieldsets = (
#         (None, {
#             'fields': ('title', 'slug', 'preacher', 'description', 'date')
#         }),
#         ('Content', {
#             'fields': ('scripture_reference', 'video_url', 'audio_file', 'document')
#         }),
#         ('Associations', {
#             'fields': ('series', 'tags')
#         }),
#         ('Settings', {
#             'fields': ('is_featured', 'image')
#         })
#     )

#     def image_preview(self, obj):
#         if obj.image:
#             return format_html('<img src="{}" style="width: 50px; height: 50px; border-radius:4px;" />', obj.image.url)
#         return "No Image"

#     image_preview.short_description = "Image Preview"


# @admin.register(Sermon)
# class SermonAdmin(admin.ModelAdmin):
#     list_display = (
#         'title', 
#         'preacher', 
#         'date', 
#         'featured', 
#         'image_preview', 
#         'facebook_url', 
#         'document',
#         'is_live'
#     )
#     list_filter = (
#         'featured', 
#         'date', 
#         'tags',  # Adjust or remove if you add series in future
#     )
#     search_fields = (
#         'title', 
#         'summary', 
#         'preacher'
#     )
#     filter_horizontal = ('tags',)
#     readonly_fields = ('slug',)
#     date_hierarchy = 'date'

#     fieldsets = (
#         (None, {
#             'fields': ('title', 'preacher', 'summary', 'date')
#         }),
#         ('Content', {
#             'fields': ('scripture_reference', 'transcript', 'facebook_url','yt_url', 'document', 'tags')
#         }),
#         ('Settings', {
#             'fields': ('featured', 'image', 'image_url', 'is_live')
#         }),
#         ('Read Only', {
#             'fields': ('slug',)
#         }),
#     )

#     def image_preview(self, obj):
#         # Check first for a locally uploaded image, then an external image URL.
#         if obj.image:
#             return format_html(
#                 '<img src="{}" style="width:50px; height:50px; border-radius:4px;" />', 
#                 obj.image.url
#             )
#         elif obj.image_url:
#             return format_html(
#                 '<img src="{}" style="width:50px; height:50px; border-radius:4px;" />', 
#                 obj.image_url
#             )
#         return "No Image"

#     image_preview.short_description = "Image Preview"


@admin.register(Sermon)
class SermonAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'preacher', 
        'date', 
        'featured', 
        'image_preview', 
        'facebook_url', 
        'document',
    )
    list_filter = (
        'featured', 
        'date', 
        'tags',  # Adjust or remove if you add series in future
    )
    search_fields = (
        'title', 
        'summary', 
        'preacher'
    )
    filter_horizontal = ('tags',)
    readonly_fields = ('slug',)
    date_hierarchy = 'date'

    fieldsets = (
        (None, {
            'fields': ('title', 'preacher', 'summary', 'date')
        }),
        ('Content', {
            'fields': ('scripture_reference', 'transcript', 'facebook_url', 'document', 'tags')
        }),
        ('Settings', {
            'fields': ('featured', 'image', 'image_url')
        }),
        ('Read Only', {
            'fields': ('slug',)
        }),
    )

    def image_preview(self, obj):
        # Check first for a locally uploaded image, then an external image URL.
        if obj.image:
            return format_html(
                '<img src="{}" style="width:50px; height:50px; border-radius:4px;" />', 
                obj.image.url
            )
        elif obj.image_url:
            return format_html(
                '<img src="{}" style="width:50px; height:50px; border-radius:4px;" />', 
                obj.image_url
            )
        return "No Image"

    image_preview.short_description = "Image Preview"




# @admin.register(SermonSeries)
# class SermonSeriesAdmin(admin.ModelAdmin):
#     list_display = ('title', 'start_date', 'end_date', 'image_preview')
#     list_filter = ('start_date', 'end_date')
#     search_fields = ('title', 'description')
#     prepopulated_fields = {'slug': ('title',)}
#     date_hierarchy = 'start_date'

#     fieldsets = (
#         (None, {
#             'fields': ('title', 'slug', 'description', 'image')
#         }),
#          ('Dates', {
#              'fields': ('start_date', 'end_date')
#          })
#     )

#     def image_preview(self, obj):
#         if obj.image:
#              return format_html('<img src="{}" style="width: 50px; height: 50px; border-radius:4px;" />', obj.image.url)
#         return "No Image"

#     image_preview.short_description = "Image Preview"


@admin.register(SermonTag)
class SermonTagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ServiceSchedule)
class ServiceScheduleAdmin(admin.ModelAdmin):
    list_display = ('service_type', 'day_of_week', 'time')
    list_filter = ('day_of_week',)
    search_fields = ('service_type', 'description')
    ordering = ['day_of_week', 'time']

    fieldsets = (
        (None, {
            'fields': ('service_type', 'day_of_week', 'time', 'description')
        }),
    )



# @admin.register(Appointment)
# class AppointmentAdmin(admin.ModelAdmin):
#     # Display key appointment information in the admin list view
#     list_display = (
#         'date', 
#         'service_type', 
#         'morning_devotion_leader', 
#         'sunday_service_leader', 
#         'tuesday_service_leader', 
#         'friday_prayer_leader'
#     )
#     list_filter = ('service_type', 'date')  # Filters for service type and date
#     search_fields = (
#         'service_type',
#         'morning_devotion_leader__user__username',
#         'sunday_service_leader__user__username',
#         'song_leader__user__username',
#         'bible_study_leader_sunday__user__username',
#         'preacher__user__username',
#         'first_prayer_leader__user__username',
#         'second_prayer_leader__user__username',
#         'third_prayer_leader__user__username',
#         'lord_supper_leader__user__username',
#         'announcer__user__username',
#         'bible_study_leader_tuesday__user__username',
#         'tuesday_service_leader__user__username',
#         'friday_prayer_leader__user__username',
#     )
#     autocomplete_fields = (
#         'morning_devotion_leader', 
#         'sunday_service_leader', 
#         'song_leader', 
#         'bible_study_leader_sunday',
#         'preacher', 
#         'first_prayer_leader', 
#         'second_prayer_leader', 
#         'third_prayer_leader', 
#         'lord_supper_leader',
#         'announcer', 
#         'bible_study_leader_tuesday', 
#         'tuesday_service_leader', 
#         'friday_prayer_leader',
#     )
#     filter_horizontal = ('lord_supper_helpers',)  # Horizontal filter for many-to-many relationships
#     date_hierarchy = 'date'  # Date hierarchy for better navigation

#     # Group fields into sections for Sunday, Tuesday, and Friday services
#     fieldsets = [
#         (None, {
#             'fields': ('date', 'service_type'),
#         }),
#         (_('Sunday Service Leaders'), {
#             'classes': ('collapse',),
#             'fields': (
#                 'morning_devotion_leader',
#                 'sunday_service_leader',
#                 'song_leader',
#                 'bible_study_leader_sunday',
#                 'preacher',
#                 'first_prayer_leader',
#                 'second_prayer_leader',
#                 'third_prayer_leader',
#                 'lord_supper_leader',
#                 'lord_supper_helpers',
#                 'announcer',
#             ),
#         }),
#         (_('Tuesday Service Leaders'), {
#             'classes': ('collapse',),
#             'fields': (
#                 'bible_study_leader_tuesday',
#                 'tuesday_service_leader',
#             ),
#         }),
#         (_('Friday Service Leaders'), {
#             'classes': ('collapse',),
#             'fields': ('friday_prayer_leader',),
#         }),
#     ]

#     # Optional: Use raw_id_fields for easier ForeignKey selection in a popup window
#     raw_id_fields = (
#         'morning_devotion_leader', 
#         'sunday_service_leader', 
#         'song_leader', 
#         'bible_study_leader_sunday',
#         'preacher', 
#         'first_prayer_leader', 
#         'second_prayer_leader', 
#         'third_prayer_leader', 
#         'lord_supper_leader',
#         'announcer', 
#         'bible_study_leader_tuesday', 
#         'tuesday_service_leader', 
#         'friday_prayer_leader',
#     )

    
#     # Add custom CSS or JavaScript if needed
#     class Media:
#         css = {
#             'all': ('admin/css/widgets.css',),  # Example of custom CSS for widgets
#         }
#         js = (
#             'https://cdnjs.cloudflare.com/ajax/libs/select2/4.1.0-rc.0/js/select2.min.js',  # Include Select2 for better dropdowns
#             'js/select2_integration.js',  # Your custom JavaScript for advanced functionality
#         )




# @admin.register(Appointment)
# class AppointmentAdmin(admin.ModelAdmin):
#     # Display key appointment information in the admin list view
#     list_display = (
#         'date', 
#         'service_type', 
#         'morning_devotion_leader', 
#         'sunday_service_leader', 
#         'tuesday_service_leader', 
#         'friday_prayer_leader'
#     )
#     list_filter = ('service_type', 'date')  # Filters for service type and date
#     search_fields = (
#         'service_type',
#         'morning_devotion_leader__user__username',
#         'sunday_service_leader__user__username',
#         'song_leader__user__username',
#         'bible_study_leader_sunday__user__username',
#         'preacher__user__username',
#         'first_prayer_leader__user__username',
#         'second_prayer_leader__user__username',
#         'third_prayer_leader__user__username',
#         'lord_supper_leader__user__username',
#         'announcer__user__username',
#         'bible_study_leader_tuesday__user__username',
#         'tuesday_service_leader__user__username',
#         'friday_prayer_leader__user__username',
#     )
#     autocomplete_fields = (
#         'morning_devotion_leader', 
#         'sunday_service_leader', 
#         'song_leader', 
#         'bible_study_leader_sunday',
#         'preacher', 
#         'first_prayer_leader', 
#         'second_prayer_leader', 
#         'third_prayer_leader', 
#         'lord_supper_leader',
#         'announcer', 
#         'bible_study_leader_tuesday', 
#         'tuesday_service_leader', 
#         'friday_prayer_leader',
#     )
#     filter_horizontal = ('lord_supper_helpers',)  # Horizontal filter for many-to-many relationships
#     date_hierarchy = 'date'  # Date hierarchy for better navigation

#     # Group fields into sections for Sunday, Tuesday, and Friday services
#     fieldsets = [
#         (None, {
#             'fields': ('date', 'service_type'),
#         }),
#         (_('Sunday Service Leaders'), {
#             'classes': ('collapse',),
#             'fields': (
#                 'morning_devotion_leader',
#                 'sunday_service_leader',
#                 'song_leader',
#                 'bible_study_leader_sunday',
#                 'preacher',
#                 'first_prayer_leader',
#                 'second_prayer_leader',
#                 'third_prayer_leader',
#                 'lord_supper_leader',
#                 'lord_supper_helpers',
#                 'announcer',
#             ),
#         }),
#         (_('Tuesday Service Leaders'), {
#             'classes': ('collapse',),
#             'fields': (
#                 'bible_study_leader_tuesday',
#                 'tuesday_service_leader',
#             ),
#         }),
#         (_('Friday Service Leaders'), {
#             'classes': ('collapse',),
#             'fields': ('friday_prayer_leader',),
#         }),
#     ]

#     # Customize foreign key and many-to-many fields
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name in [
#             'morning_devotion_leader', 
#             'sunday_service_leader', 
#             'song_leader', 
#             'bible_study_leader_sunday',
#             'preacher', 
#             'first_prayer_leader', 
#             'second_prayer_leader', 
#             'third_prayer_leader', 
#             'lord_supper_leader',
#             'announcer', 
#             'bible_study_leader_tuesday', 
#             'tuesday_service_leader', 
#             'friday_prayer_leader',
#         ]:
#             # Filter members to only show males who can lead
#             kwargs['queryset'] = Member.objects.filter(gender='M', can_lead=True)
#         elif db_field.name == 'lord_supper_helpers':
#             # Ensure only males are selected as helpers
#             kwargs['queryset'] = Member.objects.filter(gender='M')
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)
    

#     # Optional: Use raw_id_fields for easier ForeignKey selection in a popup window
#     raw_id_fields = (
#         'morning_devotion_leader', 
#         'sunday_service_leader', 
#         'song_leader', 
#         'bible_study_leader_sunday',
#         'preacher', 
#         'first_prayer_leader', 
#         'second_prayer_leader', 
#         'third_prayer_leader', 
#         'lord_supper_leader',
#         'announcer', 
#         'bible_study_leader_tuesday', 
#         'tuesday_service_leader', 
#         'friday_prayer_leader',
#     )

#     # Add custom CSS or JavaScript if needed
#     class Media:
#         css = {
#             'all': ('admin/css/widgets.css',),  # Example of custom CSS for widgets
#         }
#         js = (
#             'https://cdnjs.cloudflare.com/ajax/libs/select2/4.1.0-rc.0/js/select2.min.js',  # Include Select2 for better dropdowns
#             'js/select2_integration.js',  # Your custom JavaScript for advanced functionality
#         )

# @admin.register(Role)
# class RoleAdmin(admin.ModelAdmin):
#     list_display = ('name', 'get_allowed_days')  # Show role name and allowed days
#     search_fields = ('name',)  # Allow searching by name
#     list_filter = ('allowed_days',)  # Filter roles by allowed days
#     ordering = ('name',)

#     def get_allowed_days(self, obj):
#         return ", ".join([day.name for day in obj.allowed_days.all()])
#     get_allowed_days.short_description = "Allowed Days"


# # Inline form to assign members to multiple roles on a single page
# class AppointmentInline(admin.TabularInline):
#     model = Appointment
#     extra = 7  # Default slots for all Sunday roles
#     min_num = 1
#     verbose_name = "Role Assignment"
#     verbose_name_plural = "Role Assignments"
#     filter_horizontal = ("lord_supper_helpers", "ushers")  # User-friendly selection


# @admin.register(Day)
# class DayAdmin(admin.ModelAdmin):
#     list_display = ('name',)
#     inlines = [AppointmentInline]  # Now, you can manage all Sunday/Tuesday/Friday roles in one place!


# class LordSupperHelpersInline(admin.TabularInline):
#     model = Appointment.lord_supper_helpers.through
#     extra = 1
#     verbose_name = "Lord's Supper Helper"
#     verbose_name_plural = "Lord's Supper Helpers"


# class UshersInline(admin.TabularInline):
#     model = Appointment.ushers.through
#     extra = 1
#     verbose_name = "Usher"
#     verbose_name_plural = "Ushers"


# @admin.register(Appointment)
# class AppointmentAdmin(admin.ModelAdmin):
#     list_display = ('member_name', 'role', 'day', 'date', 'status', 'created_at')
#     list_filter = ('day', 'status', 'role')
#     search_fields = ('member__user__first_name', 'member__user__last_name', 'role__name')
#     ordering = ('-date', 'role')
#     readonly_fields = ('created_at',)
#     inlines = [LordSupperHelpersInline, UshersInline]

#     fieldsets = (
#         (_("Appointment Details"), {
#             "fields": ("member", "role", "day", "date", "status", "reason")
#         }),
#         (_("Additional Members"), {
#             "fields": ("lord_supper_helpers", "ushers"),
#             "classes": ("collapse",)
#         }),
#         (_("Timestamps"), {"fields": ("created_at",), "classes": ("collapse",)})
#     )

#     def member_name(self, obj):
#         return obj.member.user.get_full_name()
#     member_name.admin_order_field = 'member__user__first_name'
#     member_name.short_description = "Member"

#     def save_model(self, request, obj, form, change):
#         """Custom save to enforce business rules."""
#         try:
#             obj.full_clean()  # Run model validations
#         except ValidationError as e:
#             form.add_error(None, e)  # Display validation errors in admin
#             return
#         super().save_model(request, obj, form, change)

#     def get_queryset(self, request):
#         """Optimize queries by selecting related objects."""
#         return super().get_queryset(request).select_related('member', 'role')

#     filter_horizontal = ('lord_supper_helpers', 'ushers')  # User-friendly selection



@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
    

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'allowed_days_display')
    search_fields = ('name',)
    filter_horizontal = ('allowed_days',)
    ordering = ('name',)

    def allowed_days_display(self, obj):
        return ", ".join([day.name for day in obj.allowed_days.all()])
    allowed_days_display.short_description = 'Allowed Days'



# @admin.register(Appointment)
# class AppointmentAdmin(admin.ModelAdmin):
#     list_display = ('member_name', 'role', 'day', 'date', 'status', 'created_at')
#     list_filter = ('status', 'role', 'day', 'date')
#     search_fields = ('member__user__username', 'role__name', 'day__name')
#     autocomplete_fields = ('member', 'role', 'day')
#     readonly_fields = ('created_at',)
#     filter_horizontal = ('lord_supper_helpers', 'ushers')
#     list_editable = ('status',)
#     date_hierarchy = 'date'
#     ordering = ('-date',)
    
#     def get_readonly_fields(self, request, obj=None):
#         if obj:  # Prevents editing of member and role once created
#             return self.readonly_fields + ('member', 'role', 'day', 'date')
#         return self.readonly_fields

#     def save_model(self, request, obj, form, change):
#         if not change:  # If it's a new object, enforce validation
#             obj.full_clean()
#         super().save_model(request, obj, form, change)
        
#     def member_name(self, obj):
#         return obj.member.user.get_full_name()
#     member_name.admin_order_field = 'member__user__first_name'
#     member_name.short_description = "Member"

# @admin.register(Appointment)
# class AppointmentAdmin(admin.ModelAdmin):
#     list_display = ('member_name', 'role', 'day', 'date', 'status', 'created_at')
#     list_filter = ('status', 'role', 'day', 'date')
#     search_fields = ('member__user__username', 'role__name', 'day__name')
#     autocomplete_fields = ('member', 'role', 'day')
#     readonly_fields = ('created_at',)
#     # filter_horizontal = ('lord_supper_helpers', 'ushers')
#     list_editable = ('status',)
#     date_hierarchy = 'date'
#     ordering = ('-date',)

#     def save_model(self, request, obj, form, change):
#         if not change:  # If it's a new appointment, enforce validation
#             obj.full_clean()
#             self.send_appointment_email(obj)

#         super().save_model(request, obj, form, change)

#     def send_appointment_email(self, appointment):
#         """Send email notification to the appointed member"""
#         subject = "Church Appointment Notification"
#         recipient_email = appointment.member.user.email

#         # Render email content
#         context = {
#             'member_name': appointment.member.user.get_full_name(),
#             'role': appointment.role.name,
#             'day': appointment.day.name,
#             'date': appointment.date,
#         }

#         html_content = render_to_string("worship/emails/appointment_email.html", context)
#         text_content = strip_tags(html_content)  # Convert HTML to plain text

#         email = EmailMultiAlternatives(
#             subject=subject,
#             body=text_content,
#             from_email="admin@yourchurch.com",
#             to=[recipient_email]
#         )
#         email.attach_alternative(html_content, "text/html")
#         email.send()

#     def member_name(self, obj):
#         return obj.member.user.get_full_name()
#     member_name.admin_order_field = 'member__user__first_name'
#     member_name.short_description = "Member"





@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'member_name', 'role', 'day', 'date', 'status',
        'days_left', 'is_deleted', 'created_at', 'appointment_actions'
    )
    list_filter = ('status', 'role', 'day', 'date')
    search_fields = ('member__user__username', 'role__name', 'day__name', 'member__user__email')
    autocomplete_fields = ('member', 'role', 'day')
    readonly_fields = ('created_at',)
    list_editable = ('status',)
    date_hierarchy = 'date'
    ordering = ('-date',)
    actions = ['send_bulk_email', 'mark_accepted', 'mark_rejected', 'mark_deleted', 'mark_unsoftdelete']

    def get_queryset(self, request):
        """Optimize queries using select_related for foreign keys."""
        return super().get_queryset(request).select_related('member__user', 'role', 'day')

    def days_left(self, obj):
        """Display how many days are left for the appointment."""
        remaining_days = (obj.date - now().date()).days
        if remaining_days > 0:
            return format_html('<span style="color: green; font-weight: bold;">{} days left</span>', remaining_days)
        elif remaining_days == 0:
            return format_html('<span style="color: orange; font-weight: bold;">Today</span>')
        return format_html('<span style="color: red; font-weight: bold;">Past</span>')
    days_left.short_description = "Days Left"

    def appointment_actions(self, obj):
        """Inline action buttons for quick response."""
        respond_url = f"/admin/worship/appointment/{obj.id}/change/"  # Change link as necessary
        delete_url = f"/admin/worship/appointment/{obj.id}/delete/"   # Delete link as necessary
        return format_html(
            '<a href="{}" class="button" style="margin-right: 5px; background: #007bff; color: white; padding: 3px 6px; border-radius: 4px;">Edit</a>'
            '<a href="{}" class="button" style="background: #dc3545; color: white; padding: 3px 6px; border-radius: 4px;" onclick="return confirm(\'Are you sure you want to delete this appointment?\');">Delete</a>',
            respond_url, delete_url
        )
    appointment_actions.short_description = "Actions"

    def save_model(self, request, obj, form, change):
        """Custom save logic with email and notification integration."""
        try:
            if not change:  # New appointment
                obj.full_clean()
                send_email_notification(obj)  # Send email notification (utility function)
                # Create a notification with detailed appointment information
                Notification.objects.create(
                    title="New Appointment",
                    content=(
                        f"Dear {obj.member.user.get_full_name()}, you have been appointed as "
                        f"{obj.role.name} on {obj.day.name} on {obj.date.strftime('%B %d, %Y')}. "
                        "Please check your appointment section in your dashboard for more information."
                    ),
                    member=obj.member
                )
            super().save_model(request, obj, form, change)
            messages.success(request, "Appointment saved successfully!")
        except Exception as e:
            logger.error(f"Error saving appointment: {e}")
            self.message_user(request, f"Unexpected error: {e}", level=messages.ERROR)

    def member_name(self, obj):
        """Return the full name of the member."""
        return obj.member.user.get_full_name()
    member_name.admin_order_field = 'member__user__first_name'
    member_name.short_description = "Member"

    ### BULK ACTIONS ###
    @admin.action(description="📧 Send Email Notifications")
    def send_bulk_email(self, request, queryset):
        """Send email notifications to selected appointments."""
        count = 0
        failed_count = 0
        for appointment in queryset:
            try:
                send_email_notification(appointment)
                count += 1
            except Exception as e:
                logger.error(f"Error sending bulk email: {e}")
                failed_count += 1
        if count > 0:
            self.message_user(request, f"{count} email(s) sent successfully.", messages.SUCCESS)
        if failed_count > 0:
            self.message_user(request, f"Failed to send {failed_count} email(s).", messages.ERROR)

    @admin.action(description="✅ Mark as Accepted")
    def mark_accepted(self, request, queryset):
        """Mark selected appointments as 'Accepted' and notify members."""
        appointments = list(queryset)
        updated = queryset.update(status="Accepted")
        for appointment in appointments:
            Notification.objects.create(
                title="Appointment Accepted",
                content=(
                    f"Dear {appointment.member.user.get_full_name()}, your appointment on "
                    f"{appointment.date.strftime('%B %d, %Y')} has been accepted."
                ),
                member=appointment.member
            )
        self.message_user(request, f"{updated} appointments marked as 'Accepted'.", messages.SUCCESS)

    @admin.action(description="❌ Mark as Rejected")
    def mark_rejected(self, request, queryset):
        """Mark selected appointments as 'Rejected' and notify members."""
        appointments = list(queryset)
        updated = queryset.update(status="Rejected")
        for appointment in appointments:
            Notification.objects.create(
                title="Appointment Rejected",
                content=(
                    f"Dear {appointment.member.user.get_full_name()}, your appointment on "
                    f"{appointment.date.strftime('%B %d, %Y')} has been rejected."
                ),
                member=appointment.member
            )
        self.message_user(request, f"{updated} appointments marked as 'Rejected'.", messages.WARNING)

    @admin.action(description="❌ Mark as Deleted")
    def mark_deleted(self, request, queryset):
        """Mark selected appointments as 'deleted' and notify members."""
        appointments = list(queryset)
        updated = queryset.update(is_deleted=True)
        for appointment in appointments:
            Notification.objects.create(
                title="Appointment Deleted",
                content=(
                    f"Dear {appointment.member.user.get_full_name()}, your appointment on "
                    f"{appointment.date.strftime('%B %d, %Y')} has been marked as deleted."
                ),
                member=appointment.member
            )
        self.message_user(request, f"{updated} appointments marked as 'deleted'.", messages.WARNING)

    @admin.action(description="🍟 Mark as Undeleted")
    def mark_unsoftdelete(self, request, queryset):
        """Mark selected appointments as 'undeleted' and notify members."""
        appointments = list(queryset)
        updated = queryset.update(is_deleted=False)
        for appointment in appointments:
            Notification.objects.create(
                title="Appointment Restored",
                content=(
                    f"Dear {appointment.member.user.get_full_name()}, your appointment on "
                    f"{appointment.date.strftime('%B %d, %Y')} has been restored."
                ),
                member=appointment.member
            )
        self.message_user(request, f"{updated} appointments marked as 'undeleted'.", messages.WARNING)





# @admin.register(Appointment)
# class AppointmentAdmin(admin.ModelAdmin):
#     list_display = ('member', 'role', 'day', 'date', 'status')
#     list_filter = ('day', 'status', 'role')
#     search_fields = ('member__user__first_name', 'member__user__last_name', 'role__name')
#     ordering = ('-date', 'role')
#     readonly_fields = ('created_at',)

#     # Custom admin view for bulk assignments
#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('bulk-assign/', self.admin_site.admin_view(self.bulk_assign_roles), name='bulk-assign-roles'),
#         ]
#         return custom_urls + urls

#     def bulk_assign_roles(self, request):
#         """Admin page for bulk role assignments"""
#         if request.method == 'POST':
#             formset = AppointmentFormSet(request.POST)
#             if formset.is_valid():
#                 formset.save()
#                 self.message_user(request, "Appointments successfully assigned!", messages.SUCCESS)
#                 return redirect('admin:bulk-assign-roles')
#         else:
#             formset = AppointmentFormSet(queryset=Appointment.objects.none())

#         return render(request, 'admin/bulk_assign_roles.html', {'formset': formset, 'title': 'Bulk Assign Roles'})


    
# @admin.register(LiveStream)
# class LiveStreamAdmin(admin.ModelAdmin):
#     list_display = ('title', 'scheduled_time', 'is_live', 'viewers_count')
#     list_filter = ('is_live', 'scheduled_time')
#     search_fields = ('title', 'description')
#     date_hierarchy = 'scheduled_time'

#     fieldsets = (
#         (None, {
#             'fields': ('title', 'description', 'stream_url', 'scheduled_time')
#         }),
#         ('Live Stream Details', {
#             'fields': ('is_live', 'thumbnail', 'viewers_count', 'recorded_url')
#         })
#     )

# @admin.register(LiveStream)
# class LiveStreamAdmin(admin.ModelAdmin):
#     list_display  = ("title", "is_live", "created_at")
#     list_editable = ("is_live",)
#     ordering = ("-created_at",)


@admin.register(LiveStream)
class LiveStreamAdmin(admin.ModelAdmin):
    # List view enhancements
    list_display       = ("title", "is_live", "created_at")
    list_display_links = ("title",)
    list_editable      = ("is_live",)
    list_filter        = ("is_live", "created_at")
    search_fields      = ("title",)
    date_hierarchy     = "created_at"
    list_per_page      = 20
    empty_value_display = "—"
    list_select_related = ()

    # Performance tweaks
    raw_id_fields      = ()

    # Custom actions
    actions  = ("make_live", "make_offline",)

    # Form layout
    fieldsets = (
        (None, {
            "fields": ("title", "video_url", "yt_url"),
        }),
        ("Status & Timing", {
            "fields": ("is_live", "created_at"),
            "classes": ("collapse",),
        }),
    )
    readonly_fields = ("created_at",)

    # Bulk action methods
    @admin.action(description="Mark selected streams as live")
    def make_live(self, request, queryset):
        queryset.update(is_live=True)

    @admin.action(description="Mark selected streams as offline")
    def make_offline(self, request, queryset):
        queryset.update(is_live=False)

    # Default ordering
    ordering = ("-created_at",)


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'uploaded_at'

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'file')
        }),
    )

@admin.register(PrayerRequest)
class PrayerRequestAdmin(admin.ModelAdmin):
    list_display = ('member','request', 'date_requested', 'is_answered')
    list_filter = ('is_answered', 'date_requested')
    search_fields = ('member__user__username', 'request')  # Correct search field
    date_hierarchy = 'date_requested'

    fieldsets = (
        (None, {
            'fields': ('member', 'request', 'is_answered') # Correct field
        }),
    )
    
    


@admin.register(ServiceAttendance)
class ServiceAttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'date', 'day', 'total_attendance', 'males', 'females', 
        'visitors', 'absent_informed', 'absent_not_informed', 
        'students_absent', 'traveled', 'sick'
    )
    list_filter = ('day', 'date', 'total_attendance', 'visitors', 'sick')
    search_fields = ('date',)
    readonly_fields = ('total_attendance', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Service Information', {
            'fields': ('date', 'day')
        }),
        ('Attendance Breakdown', {
            'fields': ('males', 'females', 'adults', 'children', 'visitors', 'total_attendance')
        }),
        ('Absences', {
            'fields': ('absent_informed', 'absent_not_informed', 'students_absent', 'traveled', 'sick')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        """Ensures total attendance is updated before saving."""
        obj.total_attendance = obj.males + obj.females
        super().save_model(request, obj, form, change)   
