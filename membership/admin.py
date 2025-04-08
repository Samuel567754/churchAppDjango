from django.contrib import admin
from .models import Ministry, Member, Membership, Attendance, Family
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter
from datetime import date
from django.conf import settings
import os
from django.core.mail import send_mail


class AgeFilter(SimpleListFilter):
    title = 'Age Range'  # Displayed title in the admin filter sidebar
    parameter_name = 'age'  # URL query parameter name for the filter

    def lookups(self, request, model_admin):
        """Options displayed in the filter."""
        return [
            ('<18', 'Under 18'),
            ('18-35', '18-35'),
            ('36-50', '36-50'),
            ('>50', 'Above 50'),
        ]

    def queryset(self, request, queryset):
        """Filter the queryset based on the selected age range."""
        today = date.today()
        if self.value() == '<18':
            return queryset.filter(date_of_birth__gte=today.replace(year=today.year - 18))
        elif self.value() == '18-35':
            return queryset.filter(
                date_of_birth__lte=today.replace(year=today.year - 18),
                date_of_birth__gte=today.replace(year=today.year - 35)
            )
        elif self.value() == '36-50':
            return queryset.filter(
                date_of_birth__lte=today.replace(year=today.year - 36),
                date_of_birth__gte=today.replace(year=today.year - 50)
            )
        elif self.value() == '>50':
            return queryset.filter(date_of_birth__lte=today.replace(year=today.year - 50))
        return queryset







@admin.register(Ministry)
class MinistryAdmin(admin.ModelAdmin):
    list_display = ('name', 'leader', 'is_active', 'social_media_links', 'image_preview')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description', 'leader__name')
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'created_at'
    
    fieldsets = [
       (None, {
            'fields': [
                'name',
                'slug',
                 'description',
            ]
        }),
        ('Ministry Details', {
            'fields': [
                'leader',
                # 'meeting_time',
                # 'location',
                # 'meeting_schedule',
                #  'age_group',
                 'is_active',
             ]
        }),
         ('Social Media', {
                'fields': [
                    'facebook',
                    'twitter',
                    'instagram',
                    'linkedin',
                    'youtube',
                ]
            }),
            ('Image', {
                'fields': [
                    'image',
                    'image_url',
                    ]
            })
       ]

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height: 50px; width: auto;">', obj.image.url)
        elif obj.image_url:
            return format_html('<img src="{}" style="height: 50px; width: auto;">', obj.image_url)
        return "No Image"

    image_preview.short_description = "Image Preview"

    def social_media_links(self, obj):
        links = []
        if obj.facebook:
            links.append(f'<a href="{obj.facebook}" target="_blank">Facebook</a>')
        if obj.twitter:
            links.append(f'<a href="{obj.twitter}" target="_blank">Twitter</a>')
        if obj.instagram:
            links.append(f'<a href="{obj.instagram}" target="_blank">Instagram</a>')
        if obj.linkedin:
            links.append(f'<a href="{obj.linkedin}" target="_blank">LinkedIn</a>')
        if obj.youtube:
            links.append(f'<a href="{obj.youtube}" target="_blank">YouTube</a>')
        return format_html(" | ".join(links)) if links else "No Links"

    social_media_links.short_description = "Social Media Links"




@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'phone',
        'gender',
        'age',  # Display the calculated age via our custom method below
        'can_lead',
        'ministry_display',  # Custom method to display ministries
        'date_joined',
        'baptized',
        'photo_preview',
        'approval_status',
    )
    list_filter = ('gender', 'can_lead', 'approval_status', 'baptized', 'ministries', 'date_joined')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'phone')
    date_hierarchy = 'date_joined'

    fieldsets = [
        (None, {
            'fields': ['user']
        }),
        ('Member Details', {
            'fields': [
                'phone',
                'address',
                'date_of_birth',
                'gender',
                'can_lead',
                'baptized',
                'ministries',
                'approval_status',
            ]
        }),
        ('Profile Photo', {
            'fields': ['photo']
        }),
        ('Important Dates', {
            'fields': ['date_joined']
        }),
    ]
    
    readonly_fields = ('date_joined', 'age')  # Age is calculated, so it is read-only.
    
    actions = ['approve_members', 'reject_members']

    def approve_members(self, request, queryset):
        """Approve selected members."""
        queryset.update(approval_status='approved')  # Use string 'approved'
        self.send_approval_email(queryset)
        self.message_user(request, "Selected members have been approved.")

    def reject_members(self, request, queryset):
        """Reject selected members."""
        queryset.update(approval_status='rejected')  # Use string 'rejected'
        self.send_rejection_email(queryset)
        self.message_user(request, "Selected members have been rejected.")

    def send_approval_email(self, queryset):
        """Send an email to users who were approved."""
        for member in queryset:
            if member.user.email:
                send_mail(
                    'Your Membership Application Has Been Approved',
                    'Dear {},\n\nYour membership application has been approved. Welcome to our community!'.format(member.user.first_name),
                    'from@example.com',
                    [member.user.email],
                    fail_silently=False,
                )

    def send_rejection_email(self, queryset):
        """Send an email to users who were rejected."""
        for member in queryset:
            if member.user.email:
                send_mail(
                    'Your Membership Application Has Been Rejected',
                    'Dear {},\n\nWe regret to inform you that your membership application has been rejected. If you have any questions, please reach out to us.'.format(member.user.first_name),
                    'from@example.com',
                    [member.user.email],
                    fail_silently=False,
                )

    approve_members.short_description = "Approve selected members"
    reject_members.short_description = "Reject selected members"

    def photo_preview(self, obj):
        """Display a preview of the member's photo or a default image if none is uploaded."""
        if obj.photo:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; border-radius:4px;" />', 
                obj.photo.url
            )
        else:
            default_image_url = os.path.join(settings.STATIC_URL, "images/profiles/20250408_063407_0000.png")
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; border-radius:4px;" />', 
                default_image_url
            )
    photo_preview.short_description = "Photo Preview"
    
    def ministry_display(self, obj):
        return ", ".join([ministry.name for ministry in obj.ministries.all()])
    ministry_display.short_description = "Ministries"

    def age(self, obj):
        """Access the age property of the model."""
        return obj.age or "N/A"  # Return "N/A" if age is None
    age.short_description = "Age"

    def save_model(self, request, obj, form, change):
        """Validate that only male members can be marked as able to lead services."""
        if obj.can_lead and obj.gender != 'M':
            raise ValueError("Only male members can be marked as able to lead services.")
        super().save_model(request, obj, form, change)

    
@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('member_name', 'membership_type', 'join_date')  # Display member's name and membership details
    search_fields = ('member__user__username', 'membership_type')  # Search by member's username and membership type
    list_filter = ('membership_type', 'join_date')
    date_hierarchy = 'join_date'  # Add date hierarchy for join date

    def member_name(self, obj):
        # Return the full name of the member using the related User object
        return f"{obj.member.user.first_name} {obj.member.user.last_name}" if obj.member else "No Member"
    member_name.short_description = "Member Name"  # Customize the label in the admin list display

    fieldsets = [
        (None, {
            'fields': [
                'member',  # Member field
                'membership_type',  # Membership type field
                'join_date'  # Join date field
            ]
        }),
    ]
    


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('member_name', 'event', 'date', 'status')  # Display member's name, event, date, and status
    list_filter = ('status', 'date', 'event')  # Filter by status, date, and event
    search_fields = ('member__user__username', 'event__title')  # Search by member's username and event title
    actions = ['mark_as_present', 'mark_as_absent', 'mark_as_late', 'mark_as_excused']  # Custom actions
    date_hierarchy = 'date'  # Add date hierarchy for easier navigation by date
    
    fieldsets = [
        (None, {
            'fields': [
                'member',  # Assuming 'member' is a ForeignKey in Attendance model
                'event',
                'date',
                'status'
            ]
        }),
    ]

    def member_name(self, obj):
        # Return the full name of the member using the related Member object
        return f"{obj.member.user.first_name} {obj.member.user.last_name}" if obj.member else "No Member"
    member_name.short_description = "Member Name"  # Customize the label in the admin list display

    def mark_status(self, request, queryset, status):
        """Mark selected attendance records with a specific status."""
        queryset.update(status=status)
        self.message_user(request, f"{queryset.count()} attendance records marked as {status}.")
    mark_status.short_description = "Mark selected status"

    def mark_as_present(self, request, queryset):
        """Mark selected attendance records as present."""
        self.mark_status(request, queryset, 'present')
    mark_as_present.short_description = "Mark selected as present"

    def mark_as_absent(self, request, queryset):
        """Mark selected attendance records as absent."""
        self.mark_status(request, queryset, 'absent')
    mark_as_absent.short_description = "Mark selected as absent"

    def mark_as_late(self, request, queryset):
        """Mark selected attendance records as late."""
        self.mark_status(request, queryset, 'late')
    mark_as_late.short_description = "Mark selected as late"

    def mark_as_excused(self, request, queryset):
        """Mark selected attendance records as excused."""
        self.mark_status(request, queryset, 'excused')
    mark_as_excused.short_description = "Mark selected as excused"
    
    

class FamilyAdmin(admin.ModelAdmin):
    list_display = (
        'family_name', 
        'head_of_family', 
        'get_family_size', 
        'created_at', 
        'get_member_names', 
        'get_address_summary'
    )
    search_fields = ('family_name', 'head_of_family__user__username', 'members__user__username', 'address')
    list_filter = ('created_at', 'head_of_family', 'members')
    ordering = ('-created_at',)
    filter_horizontal = ('members',)

    # Display the family members in a comma-separated format
    def get_member_names(self, obj):
        return ", ".join([member.user.get_full_name() for member in obj.members.all()])
    get_member_names.short_description = 'Members'

    # Display a summary of the address in the list view
    def get_address_summary(self, obj):
        return format_html('<span title="{}">{}</span>', obj.address, obj.address[:30] + '...')
    get_address_summary.short_description = 'Address'

    # Display the family size in the list view
    def get_family_size(self, obj):
        return obj.get_family_size()
    get_family_size.short_description = 'Family Size'
    
    # Inline for editing family members directly within the family model
    class MemberInline(admin.TabularInline):
        model = Family.members.through
        extra = 1  # Number of empty forms displayed

    inlines = [MemberInline]

admin.site.register(Family, FamilyAdmin)