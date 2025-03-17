from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from contact.models import Staff, SocialMediaMixin, ImageMixin
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from datetime import date
from settings.fields import CompressedImageField


# MINISTRY MODEL
class Ministry(SocialMediaMixin, ImageMixin):
    name = models.CharField(max_length=200, unique=True, help_text="Unique name for the ministry.")
    slug = models.SlugField(unique=True, blank=True, help_text="Auto-generated from name, used in URLs.")
    description = models.TextField(help_text="A detailed description of the ministry.")
    leader = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='led_ministries', help_text="The staff member leading this ministry.")
    image_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True, help_text="Whether the ministry is currently active.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time the ministry was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date and time the ministry was last updated.")
     # meeting_time = models.CharField(max_length=100, help_text="e.g., 'Sundays 10:00 AM'")
    # location = models.CharField(max_length=200, help_text="Where the ministry meets.")
    # meeting_schedule = models.TextField(help_text="Detailed meeting schedule, including frequency and special events.")
    # age_group = models.CharField(max_length=50, blank=True, help_text="e.g., 'Youth', 'Adults', 'Seniors'")
    class Meta:
        verbose_name_plural = "Ministries"
        ordering = ['name']
        
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Member(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    APPROVAL_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, help_text="The associated user account.")
    phone = models.CharField(max_length=20, blank=True, help_text="Member's phone number.")
    address = models.TextField(blank=True, help_text="Member's full address.")
    date_of_birth = models.DateField(null=True, blank=True, help_text="Member's date of birth.")
    date_joined = models.DateField(auto_now_add=True, help_text="Date when the member joined.")
    baptized = models.BooleanField(default=False, help_text="Indicates if the member is baptized.")
   
    ministries = models.ManyToManyField(Ministry, blank=True, related_name="members", help_text="The ministries this member belongs to.")
    photo = CompressedImageField(upload_to='members/', blank=True, null=True, help_text="Member's profile picture.")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, help_text="Gender of the member.")
    can_lead = models.BooleanField(default=False, help_text="Indicates if the member can lead services (for males only).")
     # Approval Status field
    approval_status = models.CharField(
        max_length=10, choices=APPROVAL_CHOICES, default='pending'
    )

    class Meta:
        ordering = ['user__username']
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username
    
    def get_photo_url(self):
        if self.photo and hasattr(self.photo, 'url'):
            return self.photo.url
        return "/static/images/default-profile-picture.png"  # Default image path

    @property
    def age(self):
        """Calculate the member's age based on their date of birth."""
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

class Membership(models.Model):
    MEMBERSHIP_TYPES = [
        ('regular', 'Regular'),
        ('elder', 'Elder'),
        ('youth', 'Youth'),
        ('leader', 'Leader'),
        ('pastor', 'Pastor'),
    ]
    # user = models.OneToOneField(User, on_delete=models.CASCADE, help_text="The member with this membership.")
    member = models.OneToOneField(Member, on_delete=models.CASCADE, help_text="The member with this membership.")
    join_date = models.DateField(help_text="Date when the member joined with this membership.")
    membership_type = models.CharField(max_length=255, choices=MEMBERSHIP_TYPES, help_text="The type of membership the member holds.")

    class Meta:
        verbose_name_plural = "Memberships"

    def __str__(self):
        return f"{self.member.user} - {self.get_membership_type_display()}"
    

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]
    # user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="The member whose attendance is recorded.")
    member = models.ForeignKey(Member, on_delete=models.CASCADE, help_text="The member whose attendance is recorded.")
    event = models.ForeignKey(
        'event.Event', on_delete=models.CASCADE, null=True, blank=True,
        help_text="The event the attendance is for."
    )
    date = models.DateTimeField(default=timezone.now, help_text="The date and time the attendance was recorded.")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, help_text="The status of attendance.")

    class Meta:
        verbose_name_plural = "Attendance Records"
        unique_together = ('member', 'date', 'event')

    def __str__(self):
        name = self.member.user.get_full_name() or self.member.user.username
        event_name = self.event.title if self.event else "N/A"
        return f"{name} - {self.date} - {self.status} - {event_name}"
    
    
    
class Family(models.Model):
    family_name = models.CharField(max_length=255, unique=True, help_text="The name of the family.")
    address = models.TextField(blank=True, help_text="The family's address.")
    phone_number = models.CharField(max_length=20, blank=True, help_text="Family's phone number.")
    head_of_family = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, related_name="head_of_family", help_text="The head of the family (usually an elder or the first member).")
    members = models.ManyToManyField(Member, related_name="family_members", help_text="Members of this family.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date when the family was registered.")
    
    class Meta:
        verbose_name_plural = "Families"
        ordering = ['family_name']
    
    def __str__(self):
        return self.family_name

    def get_family_size(self):
        """Returns the number of members in the family."""
        return self.members.count()

    def get_family_members(self):
        """Returns a list of family members."""
        return self.members.all()

