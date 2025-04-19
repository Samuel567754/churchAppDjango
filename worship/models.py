from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from contact.models import SocialMediaMixin, ImageMixin
from contact.models import Staff
from membership.models import Member
from django.utils import timezone
from account.models import Church
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from datetime import date
from django.utils.timezone import now
from django.core.validators import FileExtensionValidator
import os
from settings.fields import CompressedImageField, SupabaseFileField
from embed_video.fields import EmbedVideoField
from datetime import timedelta

def validate_audio_file(value):
    valid_extensions = ['.mp3', '.wav', '.ogg', '.m4a']
    ext = os.path.splitext(value.name)[1]  # Get the file extension
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported audio file format. Supported formats: .mp3, .wav, .ogg, .m4a')

def validate_document_file(value):
    valid_extensions = ['.pdf', '.doc', '.docx', '.txt']
    ext = os.path.splitext(value.name)[1]
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported document format. Supported formats: .pdf, .doc, .docx, .txt')

def validate_file_size(value):
    limit = 50 * 1024 * 1024  # 50 MB
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 50 MB.')

class Service(models.Model):
    """
    Represents a church service (e.g., Sunday Morning, Bible Study).
    """
    name = models.CharField(max_length=255, help_text="Name of the service (e.g., Sunday Service)")
    day_of_week = models.IntegerField(help_text="0-6 starting with Sunday", choices=[(i, i) for i in range(7)])  # 0-6 starting with Sunday
    start_time = models.TimeField(help_text="Start time of the service")
    end_time = models.TimeField(blank=True, null=True, help_text="Optional end time of the service")
    location = models.CharField(max_length=255, blank=True, null=True, help_text="Optional location of the service")
    description = models.TextField(blank=True, null=True, help_text="Optional description of the service")
    church = models.ForeignKey(Church, on_delete=models.CASCADE, related_name='services', help_text="The church to which this service belongs")

    def __str__(self):
        return self.name
    
    def duration_hours(self):
        """Calculates the duration of the service in hours, as an integer. Returns None if no end_time"""
        if self.end_time:
            duration = (
                timezone.datetime.combine(timezone.now().date(), self.end_time) -
                timezone.datetime.combine(timezone.now().date(), self.start_time)
            )
            return int(duration.total_seconds() / 3600)
        return None


# SERVICE TYPE ENUM
# class Sermon(ImageMixin):
#     title = models.CharField(max_length=200, help_text="Title of the sermon")
#     slug = models.SlugField(unique=True, blank=True, help_text="Auto-generated from title, used in URLs.")
#     preacher = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, help_text="The staff member who preached the sermon")
#     description = models.TextField(blank=True, help_text="Description or summary of the sermon")
#     date = models.DateField(help_text="Date the sermon was preached")
#     scripture_reference = models.CharField(max_length=200, blank=True, help_text="Scripture passage reference for the sermon")
#     video_url = models.URLField(
#         blank=True,
#         null=True,
#         help_text="Optional URL to a video recording of the sermon"
#     )
    
#     audio_file = models.FileField(
#         upload_to='sermons/audio/',
#         blank=True,
#         null=True,
#         help_text="Optional audio file of the sermon",
#         validators=[validate_audio_file, validate_file_size]
#     )
    
#     document = SupabaseFileField(
#         upload_to='sermons/documents/',
#         blank=True,
#         null=True,
#         help_text="Optional document file (PDF, notes, etc.)",
#         validators=[validate_document_file, validate_file_size]
#     )
#     is_featured = models.BooleanField(default=False, help_text="Indicates if the sermon should be featured")
#     series = models.ManyToManyField('SermonSeries', blank=True, related_name='sermons', help_text="The sermon series this sermon belongs to")
#     tags = models.ManyToManyField('SermonTag', blank=True, related_name='sermons', help_text="Tags for this sermon")

#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = slugify(self.title)
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return self.title


# class SermonSeries(models.Model):
#     title = models.CharField(max_length=200, help_text="Title of the sermon series")
#     slug = models.SlugField(unique=True, blank=True, help_text="Auto-generated from title, used in URLs.")
#     description = models.TextField(blank=True, help_text="Description of the sermon series")
#     image = CompressedImageField(upload_to='sermon_series/', blank=True, null=True, help_text="Optional image for the series")
#     start_date = models.DateField(help_text="Start date of the sermon series")
#     end_date = models.DateField(null=True, blank=True, help_text="Optional end date of the sermon series")

#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = slugify(self.title)
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return self.title


class Sermon(ImageMixin):
    title = models.CharField(max_length=200)
    preacher = models.CharField(
        max_length=100,
        help_text="Name of the preacher or minister",
        default="Unknown Preacher"  # Prevents production issues by providing a default value.
    )
    date = models.DateTimeField(
        default=timezone.now,
        help_text="Date and time when the sermon was delivered"
    )
    scripture_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Scripture passage (e.g., John 3:16-18)"
    )
    summary = models.TextField(
        blank=True,
        help_text="A brief summary or outline of the sermon"
    )
    transcript = models.TextField(
        blank=True,
        help_text="Full text transcript of the sermon (optional)"
    )
    facebook_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL to the Facebook page where the sermon can be watched"
    )
    document = SupabaseFileField(
        upload_to='sermons/documents/',
        blank=True,
        null=True,
        help_text="Optional document file (PDF, notes, etc.)",
        validators=[validate_document_file, validate_file_size]
    )
    image = models.ImageField(
        upload_to='sermon_images/',
        blank=True,
        null=True,
        help_text="Upload a sermon thumbnail image"
    )
    image_url = models.URLField(
        blank=True,
        null=True,
        help_text="External URL for a sermon image (if available)"
    )
    featured = models.BooleanField(
        default=False,
        help_text="Mark this sermon as featured on the site"
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        help_text="URL-friendly version of the title",
        editable=False
    )
    # yt_url = EmbedVideoField(blank=True, null=True)
    tags = models.ManyToManyField('SermonTag', blank=True, related_name='sermons', help_text="Tags for this sermon")
    # is_live = models.BooleanField(default=False, help_text="Indicates if the sermon is currently live")

    class Meta:
        ordering = ['-date']
        verbose_name = "Sermon"
        verbose_name_plural = "Sermons"

    def __str__(self):
        return f"{self.title} by {self.preacher} on {self.date.strftime('%Y-%m-%d')}"

    def save(self, *args, **kwargs):
        # Automatically generate a unique slug based on the title.
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Sermon.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
        
        

# class Sermon(ImageMixin):
#     title = models.CharField(max_length=200)
#     preacher = models.CharField(
#         max_length=100,
#         help_text="Name of the preacher or minister",
#         default="Unknown Preacher"  # Prevents production issues by providing a default value.
#     )
#     date = models.DateTimeField(
#         default=timezone.now,
#         help_text="Date and time when the sermon was delivered"
#     )
#     scripture_reference = models.CharField(
#         max_length=100,
#         blank=True,
#         help_text="Scripture passage (e.g., John 3:16-18)"
#     )
#     summary = models.TextField(
#         blank=True,
#         help_text="A brief summary or outline of the sermon"
#     )
#     transcript = models.TextField(
#         blank=True,
#         help_text="Full text transcript of the sermon (optional)"
#     )
#     facebook_url = models.URLField(
#         blank=True,
#         null=True,
#         help_text="URL to the Facebook page where the sermon can be watched"
#     )
#     document = SupabaseFileField(
#         upload_to='sermons/documents/',
#         blank=True,
#         null=True,
#         help_text="Optional document file (PDF, notes, etc.)",
#         validators=[validate_document_file, validate_file_size]
#     )
#     image = models.ImageField(
#         upload_to='sermon_images/',
#         blank=True,
#         null=True,
#         help_text="Upload a sermon thumbnail image"
#     )
#     image_url = models.URLField(
#         blank=True,
#         null=True,
#         help_text="External URL for a sermon image (if available)"
#     )
#     featured = models.BooleanField(
#         default=False,
#         help_text="Mark this sermon as featured on the site"
#     )
#     slug = models.SlugField(
#         max_length=200,
#         unique=True,
#         blank=True,
#         help_text="URL-friendly version of the title",
#         editable=False
#     )
#     yt_url = EmbedVideoField(blank=True, null=True)
#     tags = models.ManyToManyField('SermonTag', blank=True, related_name='sermons', help_text="Tags for this sermon")
#     is_live = models.BooleanField(default=False, help_text="Indicates if the sermon is currently live")

#     class Meta:
#         ordering = ['-date']
#         verbose_name = "Sermon"
#         verbose_name_plural = "Sermons"

#     def __str__(self):
#         return f"{self.title} by {self.preacher} on {self.date.strftime('%Y-%m-%d')}"

#     def save(self, *args, **kwargs):
#         # Automatically generate a unique slug based on the title.
#         if not self.slug:
#             base_slug = slugify(self.title)
#             slug = base_slug
#             counter = 1
#             while Sermon.objects.filter(slug=slug).exists():
#                 slug = f"{base_slug}-{counter}"
#                 counter += 1
#             self.slug = slug
#         super().save(*args, **kwargs)
        
#     @property
#     def embed_html(self):
#         if self.is_live and self.facebook_url:
#             return (
#                 f'<div class="fb-video" '
#                 f'data-href="{self.facebook_url}" '
#                 f'data-width="720" '
#                 f'data-allowfullscreen="true"></div>'
#             )
#         if self.yt_url:
#             return self.yt_url   # django-embed-video tag will render this
#         return ""

#     @property
#     def needs_migration(self):
#         return (
#             not self.yt_url
#             and self.date < timezone.now() - timedelta(days=30)
#         )


class SermonTag(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text="Name of the tag")
    slug = models.SlugField(unique=True, blank=True, help_text="Auto-generated from name, used in URLs.")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# SCHEDULE MODEL
class ServiceSchedule(models.Model):
    DAYS_OF_WEEK = [
        ('Sunday', 'Sunday'),
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    ]

    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK, help_text="Day of the week for this schedule")
    time = models.TimeField(help_text="Time of the service or event")
    service_type = models.CharField(max_length=255, help_text="Type of service/event (e.g., Worship, Bible Study)")  # E.g., Worship, Bible Study
    description = models.TextField(blank=True, null=True, help_text="Optional description for the scheduled service/event")

    def __str__(self):
        return f"{self.service_type} on {self.day_of_week} at {self.time}"



class ServiceAttendance(models.Model):
    SERVICE_DAYS = [
        ('Sunday', 'Sunday'),
        ('Tuesday', 'Tuesday'),
        ('Friday', 'Friday'),
    ]

    date = models.DateField(default=now)  # Service date
    day = models.CharField(max_length=10, choices=SERVICE_DAYS)  # Day of service

    # Attendance breakdown
    total_attendance = models.PositiveIntegerField(default=0)
    males = models.PositiveIntegerField(default=0)
    females = models.PositiveIntegerField(default=0)
    adults = models.PositiveIntegerField(default=0)
    children = models.PositiveIntegerField(default=0)
    visitors = models.PositiveIntegerField(default=0)

    # Absence breakdown
    absent_informed = models.PositiveIntegerField(default=0)  # Members who informed leadership
    absent_not_informed = models.PositiveIntegerField(default=0)  # Members who didn't inform

    # Special cases
    students_absent = models.PositiveIntegerField(default=0)  # Those in school
    traveled = models.PositiveIntegerField(default=0)  # Members who traveled
    sick = models.PositiveIntegerField(default=0)  # Sick members

    # Additional field for comments
    notes = models.TextField(blank=True, null=True)

    # Auto timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('date', 'day')  # Prevent duplicate records for the same day

    def __str__(self):
        return f"{self.day} Service - {self.date.strftime('%B %d, %Y')}"

    def save(self, *args, **kwargs):
        """Automatically updates total attendance before saving."""
        self.total_attendance = self.males + self.females
        super().save(*args, **kwargs)




# class Appointment(models.Model):
#     class ServiceType(models.TextChoices):
#         SUNDAY_SERVICE = 'Sunday', 'Sunday Service'
#         TUESDAY_BIBLE_STUDY = 'Tuesday', 'Tuesday Bible Study'
#         FRIDAY_PRAYER_MEETING = 'Friday', 'Friday Prayer Meeting'

#     date = models.DateField(help_text="Date of the appointment")
#     service_type = models.CharField(
#         max_length=10,
#         choices=ServiceType.choices,
#         default=ServiceType.SUNDAY_SERVICE,
#         help_text="Type of service for the appointment",
#     )
#     morning_devotion_leader = models.ForeignKey(
#         'membership.Member', on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments_as_morning_leader', help_text="Member leading morning devotion"
#     )
#     sunday_service_leader = models.ForeignKey(
#         'membership.Member', on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments_as_sunday_service_leader', help_text="Member leading sunday service"
#     )
#     song_leader = models.ForeignKey(
#         'membership.Member', on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments_as_song_leader', help_text="Member leading songs"
#     )
#     bible_study_leader_sunday = models.ForeignKey(
#         'membership.Member', on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments_as_bible_study_leader_sunday', help_text="Member leading Bible study on Sunday"
#     )
#     preacher = models.ForeignKey(
#         'membership.Member', on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments_as_sermon_leader', help_text="Member delivering the sermon"
#     )
#     first_prayer_leader = models.ForeignKey(
#         'membership.Member', on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments_as_first_prayer_leader', help_text="Member leading the first prayer"
#     )
#     second_prayer_leader = models.ForeignKey(
#         'membership.Member', on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments_as_second_prayer_leader', help_text="Member leading the second prayer"
#     )
#     third_prayer_leader = models.ForeignKey(
#         'membership.Member', on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments_as_third_prayer_leader', help_text="Member leading the third prayer"
#     )
#     lord_supper_leader = models.ForeignKey(
#         'membership.Member', on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments_as_lord_supper_leader', help_text="Member leading the Lord's Supper"
#     )
#     lord_supper_helpers = models.ManyToManyField(
#         'membership.Member', blank=True, related_name='appointments_as_lord_supper_helpers', help_text="Members assisting with the Lord's Supper"
#     )
#     announcer = models.ForeignKey(
#         'membership.Member', on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments_as_announcer', help_text="Member making announcements"
#     )
#     bible_study_leader_tuesday = models.ForeignKey(
#         'membership.Member', on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments_as_bible_study_leader_tuesday', help_text="Member leading Bible study on Tuesday"
#     )
#     tuesday_service_leader = models.ForeignKey(
#         'membership.Member', on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments_as_tuesday_service_leader', help_text="Member leading Tuesday service"
#     )
#     friday_prayer_leader = models.ForeignKey(
#         'membership.Member', on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments_as_friday_prayer_leader', help_text="Member leading Friday prayer meeting"
#     )
#     created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time the appointment was created")
#     updated_at = models.DateTimeField(auto_now=True, help_text="Date and time the appointment was last updated")

#     class Meta:
#         ordering = ['-date']
#         constraints = [
#             models.UniqueConstraint(fields=['date', 'service_type'], name='unique_appointment')
#         ]

#     def __str__(self):
#         return f"{self.service_type} - {self.date}"



# from django.db import models
# from django.core.exceptions import ValidationError
# from datetime import date

# class ServiceType(models.TextChoices):
#     SUNDAY_SERVICE = 'Sunday', 'Sunday Service'
#     TUESDAY_BIBLE_STUDY = 'Tuesday', 'Tuesday Bible Study'
#     FRIDAY_PRAYER_MEETING = 'Friday', 'Friday Prayer Meeting'

# class Appointment(models.Model):
#     date = models.DateField(help_text="Date of the appointment")
#     service_type = models.CharField(
#         max_length=15,  # Increased length for flexibility
#         choices=ServiceType.choices,
#         default=ServiceType.SUNDAY_SERVICE,
#         help_text="Type of service for the appointment",
#     )
#     members = models.ManyToManyField(
#         'membership.Member',
#         through='AppointmentRole',
#         help_text="Members assigned to roles for this appointment"
#     )
#     created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time the appointment was created")
#     updated_at = models.DateTimeField(auto_now=True, help_text="Date and time the appointment was last updated")

#     class Meta:
#         ordering = ['-date']
#         constraints = [
#             models.UniqueConstraint(fields=['date', 'service_type'], name='unique_appointment')
#         ]

#     def __str__(self):
#         return f"{self.service_type} - {self.date}"

#     def clean(self):
#         """Ensure the appointment date aligns with the service type"""
#         if self.date.strftime('%A') != self.service_type:
#             raise ValidationError({'date': f"The selected date must be a {self.service_type}."})

#         # Prevent past appointments
#         if self.date < date.today():
#             raise ValidationError({'date': 'Cannot schedule an appointment for a past date.'})

#     def save(self, *args, **kwargs):
#         self.full_clean()  # Run validations before saving
#         super().save(*args, **kwargs)

class Day(models.Model):
    """Defines available service days dynamically"""
    MONDAY = 'Monday'
    SUNDAY = 'Sunday'
    TUESDAY = 'Tuesday'
    FRIDAY = 'Friday'

    DAY_CHOICES = [
        (MONDAY, 'Monday'),
        (SUNDAY, 'Sunday'),
        (TUESDAY, 'Tuesday'),
        (FRIDAY, 'Friday'),
    ]

    name = models.CharField(max_length=10, unique=True, choices=DAY_CHOICES)

    def __str__(self):
        return self.name


class Role(models.Model):
    """Defines church service roles and allowed service days"""
    name = models.CharField(max_length=50, unique=True)
    allowed_days = models.ManyToManyField(Day, related_name="roles")  # Many-to-Many for flexibility

    def __str__(self):
        return self.name


class Appointment(models.Model):
    """Manages role assignments for specific service days"""
    STATUS_PENDING = 'Pending'
    STATUS_ACCEPTED = 'Accepted'
    STATUS_DENIED = 'Denied'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_DENIED, 'Denied'),
    ]

    REASON_CHOICES = [
        ('Health Issues', 'Health Issues'),
        ('Work Commitment', 'Work Commitment'),
        ('Family Emergency', 'Family Emergency'),
        ('Traveling', 'Traveling'),
        ('Other', 'Other'),
    ]

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        limit_choices_to={'gender': 'M'}  # Restrict to males
    )
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    reason = models.CharField(
        max_length=50,
        choices=REASON_CHOICES,
        blank=True,
        null=True,
        help_text="Required if appointment is denied."
    )
    reminder_sent = models.BooleanField(default=False)
    
    is_archived = models.BooleanField(default=False)  # Track old appointments

    created_at = models.DateTimeField(auto_now_add=True)

    is_deleted = models.BooleanField(default=False)  # Soft delete field

    class Meta:
        unique_together = ['date', 'role', 'member']
        ordering = ['-date']

    def __str__(self):
        return f"{self.member} - {self.role.name} on {self.date} ({self.status})"
    
    def days_left(self):
        """Calculate days left for the appointment"""
        days_remaining = (self.date - now().date()).days
        return days_remaining if days_remaining >= 0 else None

    def is_past(self):
        """Check if the appointment date has passed"""
        return self.date < now().date()
    
    def can_delete(self):
        """Returns True if the appointment can be deleted by the member."""
        if self.status == self.STATUS_PENDING:
            return False  # Hide delete button for pending appointments
        if self.status == self.STATUS_DENIED:
            return True  # Allow delete for denied appointments
        if self.status == self.STATUS_ACCEPTED and self.date < now().date():
            return True  # Allow delete after the appointment date has passed
        return False

    def clean(self):
        """Ensures proper validation before saving an appointment"""
        if self.status == self.STATUS_DENIED and not self.reason:
            raise ValidationError({'reason': 'Reason is required when status is Denied.'})

        if not self.role.allowed_days.filter(name=self.day.name).exists():
            raise ValidationError({'role': f'{self.role.name} is not assigned to {self.day.name} services.'})

        if self.date.strftime('%A') != self.day.name:
            raise ValidationError({'date': f'Date must be a {self.day.name}. Selected date is {self.date.strftime("%A")}.'})

        if self.date < date.today() and not self.is_deleted:
            raise ValidationError({'date': 'Cannot create appointments for past dates.'})

    def save(self, *args, **kwargs):
        self.full_clean()  # Ensure validations are run before saving
        super().save(*args, **kwargs)






class Schedule(models.Model):
    RECURRING_CHOICES = [
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('YEARLY', 'Yearly'),
    ]

    title = models.CharField(max_length=200, help_text="Title of the schedule")
    description = models.TextField(blank=True, help_text="Description of the schedule")
    start_time = models.DateTimeField(help_text="Start time for the event on schedule")
    end_time = models.DateTimeField(help_text="End time for the event on the schedule")
    location = models.CharField(max_length=200, blank=True, help_text="Optional location for the event")
    is_recurring = models.BooleanField(default=False, help_text="Indicates if the schedule is recurring")
    recurrence_pattern = models.CharField(
        max_length=100,
        choices=RECURRING_CHOICES,
        blank=True,
        help_text="E.g., 'Weekly', 'Monthly', 'Yearly' (if the schedule is recurring)",
    )

    def __str__(self):
        return self.title


# class LiveStream(models.Model):
#     title = models.CharField(max_length=200, help_text="Title of the live stream")
#     description = models.TextField(help_text="Description of the live stream")
#     stream_url = models.URLField(help_text="URL of the live stream")
#     scheduled_time = models.DateTimeField(help_text="Scheduled time for the live stream")
#     is_live = models.BooleanField(default=False, help_text="Indicates if the live stream is currently live")
#     thumbnail = CompressedImageField(upload_to='livestreams/', help_text="Thumbnail for the live stream")
#     viewers_count = models.IntegerField(default=0, help_text="Current count of viewers for the live stream")
#     recorded_url = models.URLField(blank=True, null=True, help_text="Optional URL to the recorded version of the live stream")

#     def __str__(self):
#         return self.title


class LiveStream(models.Model):
    title = models.CharField(
            max_length=200,
            help_text="Title of the live stream"
            )
    video_url = models.URLField(blank=True, null=True,
            help_text="Public Facebook video post URL"
            )
    yt_url  = EmbedVideoField(
                   blank=True,
                   null=True,
                   help_text="YouTube replay URL (after FB expires)"
               )
    is_live = models.BooleanField(
            default=False, 
            help_text="Whether this stream is currently live"
            )
    created_at = models.DateTimeField(
            auto_now_add=True,
            help_text="When this entry was created"
            )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
    
    # @property
    # def needs_migration(self):
    #     return (
    #         not self.yt_url
    #         and self.date < timezone.now() - timedelta(days=30)
    #     )
    
    def needs_migration(self):
        return (
            not self.yt_url
            and self.date < timezone.now() - timedelta(days=30)
        )


class Resource(models.Model):
    title = models.CharField(max_length=255, help_text="Title of the resource")
    description = models.TextField(help_text="Description of the resource")
    file = SupabaseFileField(upload_to='resources/', help_text="Upload the resource file",validators=[validate_document_file, validate_file_size])
    uploaded_at = models.DateTimeField(auto_now_add=True, help_text="Date and time the resource was uploaded")

    def __str__(self):
        return self.title
    
    
class PrayerRequest(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="User who requested prayer")
    member = models.ForeignKey(Member, on_delete=models.CASCADE, help_text="Member who requested prayer", related_name='prayer_requests',null=True, blank=True,)
    request = models.TextField(help_text="Details of the prayer request")
    date_requested = models.DateTimeField(auto_now_add=True, help_text="Date and time the prayer request was made")
    is_answered = models.BooleanField(default=False, help_text="Indicates if the prayer request has been answered")

    def __str__(self):
        return f"Prayer Request by {self.member.user}"


# Signals

@receiver(pre_save, sender=Sermon)
def set_sermon_slug(sender, instance, **kwargs):
    """
    Automatically sets the slug for a sermon before saving.
    """
    if not instance.slug:
        instance.slug = slugify(instance.title)


# @receiver(pre_save, sender=SermonSeries)
# def set_sermon_series_slug(sender, instance, **kwargs):
#     """
#     Automatically sets the slug for a sermon series before saving.
#     """
#     if not instance.slug:
#         instance.slug = slugify(instance.title)

@receiver(pre_save, sender=SermonTag)
def set_sermon_tag_slug(sender, instance, **kwargs):
    """
    Automatically sets the slug for a sermon tag before saving.
    """
    if not instance.slug:
         instance.slug = slugify(instance.name)
         
         
         
         



# from django.core.exceptions import ValidationError
# from django.db import models
# from django.utils.timezone import now
# from datetime import date

# class Appointment(models.Model):
#     """Manages role assignments for specific service days"""
    
#     STATUS_PENDING = 'Pending'
#     STATUS_ACCEPTED = 'Accepted'
#     STATUS_DENIED = 'Denied'

#     STATUS_CHOICES = [
#         (STATUS_PENDING, 'Pending'),
#         (STATUS_ACCEPTED, 'Accepted'),
#         (STATUS_DENIED, 'Denied'),
#     ]

#     REASON_CHOICES = [
#         ('Health Issues', 'Health Issues'),
#         ('Work Commitment', 'Work Commitment'),
#         ('Family Emergency', 'Family Emergency'),
#         ('Traveling', 'Traveling'),
#         ('Other', 'Other'),
#     ]

#     member = models.ForeignKey(
#         Member,
#         on_delete=models.CASCADE,
#         limit_choices_to={'gender': 'M'}  # Restrict to males
#     )
#     role = models.ForeignKey(Role, on_delete=models.CASCADE)
#     day = models.ForeignKey(Day, on_delete=models.CASCADE)
#     date = models.DateField()
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
#     reason = models.CharField(
#         max_length=50,
#         choices=REASON_CHOICES,
#         blank=True,
#         null=True,
#         help_text="Required if appointment is denied."
#     )
#     reminder_sent = models.BooleanField(default=False)
#     is_archived = models.BooleanField(default=False)  # Track old appointments
#     created_at = models.DateTimeField(auto_now_add=True)
#     is_deleted = models.BooleanField(default=False)  # Soft delete field

#     class Meta:
#         ordering = ['-date']

#     def __str__(self):
#         return f"{self.member} - {self.role.name} on {self.date} ({self.status})"

#     def days_left(self):
#         """Calculate days left for the appointment"""
#         days_remaining = (self.date - now().date()).days
#         return days_remaining if days_remaining >= 0 else None

#     def is_past(self):
#         """Check if the appointment date has passed"""
#         return self.date < now().date()
    
#     def can_delete(self):
#         """Returns True if the appointment can be deleted by the member."""
#         if self.is_past() or self.status == self.STATUS_DENIED:
#             return True
#         return False

#     def clean(self):
#         """Ensures proper validation before saving an appointment"""
#         if self.status == self.STATUS_DENIED and not self.reason:
#             raise ValidationError({'reason': 'Reason is required when status is Denied.'})

#         if not self.role.allowed_days.filter(name=self.day.name).exists():
#             raise ValidationError({'role': f'{self.role.name} is not assigned to {self.day.name} services.'})

#         if self.date.weekday() != ['Monday', 'Sunday', 'Tuesday', 'Friday'].index(self.day.name):
#             raise ValidationError({'date': f'Date must be a {self.day.name}. Selected date is {self.date.strftime("%A")}.'})

#         if self.date < date.today() and not self.is_deleted:
#             raise ValidationError({'date': 'Cannot create appointments for past dates.'})

#     def delete(self, *args, **kwargs):
#         """Implements soft delete instead of permanently deleting the object."""
#         self.is_deleted = True
#         self.save()
