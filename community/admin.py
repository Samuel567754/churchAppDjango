from django.contrib import admin
from django.utils.html import format_html
from .models import (
    VolunteerOpportunity, VolunteerApplication, Testimonial,
    FAQ, Survey, SurveyResponse, Poll, PollOption, PollVote, Announcement,
    CarouselItem, Devotional
)
from contact.models import Notification  # Adjust import based on your project structure


class PollOptionInline(admin.TabularInline):
    model = PollOption
    extra = 1

class VolunteerApplicationInline(admin.TabularInline):
    model = VolunteerApplication
    extra = 1


@admin.register(CarouselItem)
class CarouselItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'image_preview', 'description_preview', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    ordering = ['order']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height: 50px; width: auto;">', obj.image.url)
        elif obj.image_url:
            return format_html('<img src="{}" style="height: 50px; width: auto;">', obj.image_url)
        return "No Image"

    image_preview.short_description = 'Image Preview'

    def description_preview(self, obj):
        if obj.description:
            return obj.description[:50] + ('...' if len(obj.description) > 50 else '')
        return "No Description"

    description_preview.short_description = 'Description'

    def save_model(self, request, obj, form, change):
        obj.full_clean()  # Validate fields
        super().save_model(request, obj, form, change)

@admin.register(VolunteerOpportunity)
class VolunteerOpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'ministry', 'is_active', 'start_date', 'end_date', 'created_by_name')
    search_fields = ('title', 'description', 'ministry__name', 'created_by__first_name', 'created_by__last_name')
    list_filter = ('ministry', 'is_active', 'start_date')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = [
        ('Opportunity Details', {
            'fields': ['title', 'slug', 'description', 'start_date', 'end_date', 'location', 'ministry', 'is_active'],
            'classes': ['wide', 'extrapretty']
        }),
        ('Additional Information', {
            'fields': ['created_by'],
             'classes': ['collapse','extrapretty'],

        }),
    ]
    inlines = [VolunteerApplicationInline]

    def created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else "N/A"
    created_by_name.short_description = 'Created By'

@admin.register(VolunteerApplication)
class VolunteerApplicationAdmin(admin.ModelAdmin):
    list_display = ('member_name', 'opportunity', 'application_date', 'accepted', 'notes_preview')
    search_fields = ('member__user__username', 'opportunity__title')
    list_filter = ('accepted', 'application_date')

    def member_name(self, obj):
        # Display the member's full name
        return f"{obj.member.user.first_name} {obj.member.user.last_name}" if obj.member else "No Member"
    member_name.short_description = "Member Name"

    def notes_preview(self, obj):
        # Display a short preview of the notes
        return obj.notes[:50] + "..." if obj.notes else "N/A"
    notes_preview.short_description = "Notes"
    
    
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('member_name', 'approved', 'date_submitted', 'content_preview')
    list_filter = ('approved', 'date_submitted')
    search_fields = ('member__user__username', 'content')  # Search by member's username
    fieldsets = [
        ("Testimonial", {
            "fields": ['member', 'content', 'approved'],
            'classes': ['extrapretty']
        })
    ]

    def member_name(self, obj):
        # Display the member's full name
        return f"{obj.member.user.first_name} {obj.member.user.last_name}" if obj.member else "Anonymous"
    member_name.short_description = "Member Name"

    def content_preview(self, obj):
        # Preview of the content
        return obj.content[:50] + "..." if obj.content else "No Content"
    content_preview.short_description = "Content"
    

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('question', 'answer')
    fieldsets = [
        (None, {
            'fields': ['question', 'answer', 'is_active', 'order'],
            'classes': ['extrapretty']
        })
    ]


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'description_preview')
    search_fields = ('title', 'description')
    fieldsets = [
        (None, {
            'fields': ['title', 'description'],
            'classes': ['wide', 'extrapretty']
        })
    ]

    def description_preview(self, obj):
        return obj.description[:50] + "..." if obj.description else "N/A"
    description_preview.short_description = "Description"



@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ('survey', 'member_name', 'submitted_at', 'response_preview')
    search_fields = ('survey__title', 'member__user__username', 'response')  # Search by member's username
    list_filter = ('submitted_at',)

    def member_name(self, obj):
        # Display the member's full name
        return f"{obj.member.user.first_name} {obj.member.user.last_name}" if obj.member else "No Member"
    member_name.short_description = "Member Name"

    def response_preview(self, obj):
        # Display a short preview of the response
        return obj.response[:50] + "..." if obj.response else "N/A"
    response_preview.short_description = "Response"




# @admin.register(OutreachProgram)
# class OutreachProgramAdmin(admin.ModelAdmin):
#     list_display = ('name', 'start_date', 'end_date', 'is_active', 'location')
#     list_filter = ('is_active', 'start_date', 'end_date')
#     search_fields = ('name', 'description', 'location')

#     fieldsets = [
#         ('Program Details', {
#             'fields': ['name', 'description', 'start_date', 'end_date', 'location', 'is_active', 'organizers'],
#             'classes': ['extrapretty']
#         })
#     ]

# Registering the Poll model
@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('question', 'is_active', 'created_at')
    search_fields = ('question',)
    list_filter = ('is_active', 'created_at')
    inlines = [PollOptionInline]

    fieldsets = [
        (None, {
            'fields': ['question', 'is_active'],
            'classes': ['extrapretty']
        })
    ]


# Registering the PollOption model
@admin.register(PollOption)
class PollOptionAdmin(admin.ModelAdmin):
    list_display = ('poll', 'option_text')
    search_fields = ('option_text',)
    list_filter = ('poll',)


@admin.register(PollVote)
class PollVoteAdmin(admin.ModelAdmin):
    list_display = ('member_name', 'option', 'get_poll')
    search_fields = ('member__user__username', 'option__option_text', 'option__poll__question')  # Search by member's username
    list_filter = ('option__poll',)

    def member_name(self, obj):
        # Display the member's full name
        return f"{obj.member.user.first_name} {obj.member.user.last_name}" if obj.member else "No Member"
    member_name.short_description = "Member Name"

    def get_poll(self, obj):
        # Get the associated poll
        return obj.option.poll
    get_poll.short_description = "Poll"



@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'importance_level', 'date_posted', 'is_active', 'content_preview')
    list_filter = ('status', 'importance_level', 'is_active')
    search_fields = ('title', 'content')
    fieldsets = [
        ("Announcement Details", {
            'fields': ['title', 'content', 'status', 'importance_level', 'is_active'],
            'classes': ['extrapretty']
        })
    ]

    def content_preview(self, obj):
        return obj.content[:50] + "..."
    content_preview.short_description = "Content"

    def save_model(self, request, obj, form, change):
        # Optionally, store previous state to detect changes
        previous = None
        if change:
            previous = Announcement.objects.get(pk=obj.pk)
        super().save_model(request, obj, form, change)

        # Create a notification if the announcement is active.
        # This example creates a notification when an announcement is created,
        # or when an existing announcement is updated from inactive to active.
        if obj.is_active:
            if not change or (previous and not previous.is_active):
                Notification.objects.create(
                    title=obj.title,
                    content=obj.content,
                    member=None  # A general notification (not member-specific)
                )
                



@admin.register(Devotional)
class DevotionalAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'published', 'is_featured', 'image_link', 'published_at', 'created_at')
    list_filter = ('published', 'is_featured', 'date')
    search_fields = ('title', 'summary', 'content', 'scripture_reference')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-date',)

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'summary', 'content', 'scripture_reference', 'image_url')
        }),
        ('Scheduling and Status', {
            'fields': ('date', 'is_featured', 'published', 'published_at'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'published_at')

    def image_link(self, obj):
        """Returns an HTML link to the image if image_url exists."""
        if obj.image_url:
            return format_html('<a href="{0}" target="_blank">View Image</a>', obj.image_url)
        return "-"
    image_link.short_description = 'Image Link'