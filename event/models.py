from django.db import models
from django.contrib.auth.models import User
from contact.models import Staff
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from django.utils.timezone import now
from contact.models import SocialMediaMixin, ImageMixin
from django.db.models.signals import pre_save
from django.dispatch import receiver
from membership.models import Member
from django.urls import reverse

# EVENT MODEL
class Event(ImageMixin):
    EVENT_TYPES = [
        ('service', 'Church Service'),
        ('workshop', 'Workshop'),
        ('youth', 'Youth Event'),
        ('community', 'Community Event'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    organizer = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)
    registration_required = models.BooleanField(default=False)
    max_attendees = models.PositiveIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1)]
    )
    featured = models.BooleanField(default=False)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    # attendees = models.ManyToManyField(User, through='EventRegistration', blank=True)
    attendees = models.ManyToManyField(Member, through='EventRegistration', blank=True)  # Use Member here
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['-date']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    
# IMAGE GALLERY
class GalleryImage(ImageMixin):
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=50, blank=True)  # New category field
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title if self.title else "Unnamed Image"


class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, null=True)  # Updated to use Member
    registration_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['event', 'member']  # Update unique_together
        ordering = ['-registration_date']

    def __str__(self):
        return f"{self.member.user.username} registered for {self.event.title}"  # Access Member's related User



class OutreachProgram(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=255)
    organizers = models.ManyToManyField(Staff, related_name='outreach_programs')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# class ChurchCalendar(models.Model):
#     title = models.CharField(max_length=255)
#     date = models.DateField()
#     time = models.TimeField()
#     description = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['date', 'time']

#     def __str__(self):
#         return f"{self.title} on {self.date}"



class ChurchCalendar(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'time']
        verbose_name = "Church Calendar Event"
        verbose_name_plural = "Church Calendar Events"

    def __str__(self):
        return f"{self.title} on {self.date} at {self.time}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('church_calendar_detail', args=[self.slug])



# SIGNALS
@receiver(pre_save, sender=Event)
def set_event_slug(sender, instance, **kwargs):
    """
    Automatically sets the slug for an event before saving.
    """
    if not instance.slug:
        instance.slug = slugify(instance.title)


@receiver(pre_save, sender=OutreachProgram)
def set_outreach_program_slug(sender, instance, **kwargs):
    """
    Automatically sets the slug for an outreach program before saving.
    """
    if not instance.slug:
        instance.slug = slugify(instance.name)
