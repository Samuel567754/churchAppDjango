from django.contrib import admin
from .models import Event, EventRegistration, OutreachProgram, ChurchCalendar, GalleryImage
from django.utils.html import format_html


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date','featured',  'event_type', 'organizer', 'registration_required', 'max_attendees', 'image_preview')
    list_filter = ('event_type', 'featured', 'registration_required', 'date')
    # search_fields = ('title', 'description', 'organizer__name')
    search_fields = ('title', 'description', 'organizer__name', 'attendees__user__username')  # Search attendees by username
    prepopulated_fields = {'slug': ('title',)}
    actions = ['mark_as_registration_required', 'unmark_as_registration_required']
    date_hierarchy = 'date'
    
    fieldsets = [
            (None, {
                'fields': [
                    'title',
                    'slug',
                    'description',
                ]
            }),
            ('Event Details', {
                'fields': [
                    'date',
                    'featured', 
                    'end_date',
                    'location',
                    'event_type',
                    'organizer',
                ]
            }),
            ('Registration Settings', {
                'fields': [
                    'registration_required',
                    'max_attendees',
                ]
            }),
            ('Image', {
                'fields': ['image']
            })
        ]


    def image_preview(self, obj):
            if obj.image:
                return format_html('<img src="{}" style="width: 50px; height: 50px; border-radius:4px;" />', obj.image.url)
            return "No Image"

    image_preview.short_description = "Image Preview"

    def mark_as_registration_required(self, request, queryset):
        queryset.update(registration_required=True)
        self.message_user(request, f"{queryset.count()} events updated to require registration.")
    mark_as_registration_required.short_description = "Mark selected as require registration"

    def unmark_as_registration_required(self, request, queryset):
        queryset.update(registration_required=False)
        self.message_user(request, f"{queryset.count()} events updated to not require registration.")
    unmark_as_registration_required.short_description = "Mark selected as not require registration"



@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at', 'category', 'is_featured', 'image_preview')
    list_filter = ('is_featured', 'category')
    search_fields = ('title', 'description')
    actions = ['mark_as_featured', 'unmark_as_featured']
    date_hierarchy = 'uploaded_at'

    fieldsets = [
        (None, {
            'fields': [
                'title',
                'description',
                'category',
                'image',
                'is_featured'
            ]
        }),
    ]

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; border-radius:4px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = "Image Preview"

    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f"{queryset.count()} images marked as featured.")
    mark_as_featured.short_description = "Mark selected images as featured"

    def unmark_as_featured(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, f"{queryset.count()} images unmarked as featured.")
    unmark_as_featured.short_description = "Unmark selected images as featured"



# @admin.register(EventRegistration)
# class EventRegistrationAdmin(admin.ModelAdmin):
#     list_display = ('event', 'user', 'registration_date')
#     search_fields = ('event__title', 'user__username')
#     date_hierarchy = 'registration_date'


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('event', 'member_name', 'registration_date')  # Display member's name
    search_fields = ('event__title', 'member__user__username')  # Search by member's username
    date_hierarchy = 'registration_date'

    def member_name(self, obj):
        return f"{obj.member.user.first_name} {obj.member.user.last_name}"  # Display Member's User name
    member_name.short_description = "Member Name"
    
    
    
    

    
@admin.register(OutreachProgram)
class OutreachProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('name', 'description', 'location')
    prepopulated_fields = {'slug': ('name',)}
    actions = ['mark_as_active', 'mark_as_inactive']
    date_hierarchy = 'start_date'

    fieldsets = [
            (None, {
                'fields': [
                    'name',
                    'slug',
                    'description',
                ]
            }),
            ('Details', {
                'fields': [
                    'start_date',
                    'end_date',
                    'location',
                    'organizers',
                    'is_active',
                ]
            }),
        ]

    def mark_as_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} outreach programs marked as active.")
    mark_as_active.short_description = "Mark selected programs as active"

    def mark_as_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} outreach programs marked as inactive.")
    mark_as_inactive.short_description = "Mark selected programs as inactive"




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


# @admin.register(ChurchCalendar)
# class ChurchCalendarAdmin(admin.ModelAdmin):
#     list_display = ('title', 'date', 'time', 'created_at', 'updated_at')
#     search_fields = ('title', 'description')
#     list_filter = ('date',)
#     date_hierarchy = 'date'
    
#     # Automatically populate slug from title
#     prepopulated_fields = {'slug': ('title',)}
    
#     # Make timestamps read-only in the admin
#     readonly_fields = ('created_at', 'updated_at')
    
#     fieldsets = (
#         (None, {
#             'fields': ('title', 'slug', 'description'),
#         }),
#         ('Event Details', {
#             'fields': ('date', 'time'),
#         }),
#         ('Timestamps', {
#             'fields': ('created_at', 'updated_at'),
#             'classes': ('collapse',),  # Collapsible section for cleaner UI
#         }),
#     )




# @admin.register(ChurchCalendar)
# class ChurchCalendarAdmin(admin.ModelAdmin):
#     list_display = ('title', 'start_datetime', 'end_datetime', 'category', 'location', 'featured')
#     list_filter = ('category', 'featured', 'start_datetime')
#     search_fields = ('title', 'description', 'location')
#     prepopulated_fields = {"slug": ("title",)}
#     ordering = ('start_datetime',)
    
#     fieldsets = (
#         (None, {
#             'fields': ('title', 'slug', 'category', 'location', 'featured')
#         }),
#         ('Event Timing', {
#             'fields': ('start_datetime', 'end_datetime', 'all_day'),
#         }),
#         ('Event Details', {
#             'fields': ('description',),
#         }),
#         ('Timestamps', {
#             'fields': ('created_at', 'updated_at'),
#             'classes': ('collapse',),
#         }),
#     )
#     readonly_fields = ('created_at', 'updated_at')
      
    

@admin.register(ChurchCalendar)
class ChurchCalendarAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'start_datetime', 
        'end_datetime', 
        'category', 
        'location', 
        'featured', 
        'display_image'
    )
    list_filter = ('category', 'featured', 'start_datetime')
    search_fields = ('title', 'description', 'location')
    prepopulated_fields = {"slug": ("title",)}
    ordering = ('start_datetime',)
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'location', 'featured')
        }),
        ('Event Timing', {
            'fields': ('start_datetime', 'end_datetime', 'all_day'),
        }),
        ('Event Details', {
            'fields': ('description',),
        }),
        ('Image', {
            'fields': ('image', 'image_url', 'display_image'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'display_image')
    
    def display_image(self, obj):
        """
        This method renders the image from the model.
        It first checks if an uploaded image exists (from ImageMixin).
        If not, it falls back to the external image URL.
        """
        if obj.image:
            url = obj.image.url
        elif obj.image_url:
            url = obj.image_url
        else:
            return "-"
        return format_html('<img src="{}" alt="{}" style="max-width:100px; max-height:100px;" />', url, obj.title)
    display_image.short_description = 'Image'