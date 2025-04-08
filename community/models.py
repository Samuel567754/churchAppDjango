from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from membership.models import Ministry, Member
from contact.models import Staff
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver
from settings.fields import CompressedImageField
from django.utils import timezone


class VolunteerOpportunity(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    slug = models.SlugField(unique=True)
    end_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    ministry = models.ForeignKey(Ministry, on_delete=models.SET_NULL, null=True, blank=True, related_name="volunteer_opportunities")
    created_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_opportunities")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('volunteer_opportunity_detail', args=[self.id])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

# TESTIMONIALS
class Testimonial(models.Model):
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name="testimonials")  # Changed to Member
    content = models.TextField()
    date_submitted = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Testimonial by {self.member.user.get_full_name() if self.member else 'Anonymous'}"  # Access Member's related User


# FAQ
class FAQ(models.Model):
    question = models.CharField(max_length=200)
    answer = models.TextField()
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.question


# SURVEYS AND RESPONSES
class Survey(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('survey_detail', args=[self.id])


# POLL MODEL
class Poll(models.Model):
    question = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.question


# POLL OPTION MODEL
class PollOption(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.option_text} (Poll: {self.poll})"

    
    
class Announcement(models.Model):
    # Choices for announcement status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    # Choices for importance level
    IMPORTANCE_CHOICES = [
        ('urgent', 'Urgent'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',  # Default status is 'draft'
    )
    importance_level = models.CharField(
        max_length=10,
        choices=IMPORTANCE_CHOICES,
        default='medium',  # Default importance level is 'medium'
    )

    def __str__(self):
        return self.title
    
    

class CarouselItem(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = CompressedImageField(upload_to='carousel_images/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)  # Optional link for the carousel item
    is_active = models.BooleanField(default=True)  # To control visibility
    order = models.PositiveIntegerField(default=0)  # To control order of items

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title or f"Carousel Item {self.id}"

    def clean(self):
        # Ensure at least one of image or image_url is provided
        if not self.image and not self.image_url:
            raise ValidationError("Either 'image' or 'image_url' must be provided.")
        

# POLL VOTE
class PollVote(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)  # Changed to Member
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE)
    poll = models.ForeignKey('Poll', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.member.user.username} voted for {self.option}"  # Access Member's related User


# SURVEY RESPONSE
class SurveyResponse(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="responses")
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="survey_responses")  # Updated to use Member
    response = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response to {self.survey.title} by {self.member.user.username}"  # Access Member's related User

# VOLUNTEER APPLICATION
class VolunteerApplication(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="volunteer_applications")
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    opportunity = models.ForeignKey(VolunteerOpportunity, on_delete=models.CASCADE, related_name="applications")
    application_date = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['member', 'opportunity']

    def __str__(self):
        return f"{self.member.user.username}applied for {self.opportunity.title}" # Access Member's related User


class Devotional(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    summary = models.TextField(blank=True, null=True, help_text="A short summary of the devotional.")
    content = models.TextField()
    scripture_reference = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True, help_text="Optional URL for the devotional image.")
    date = models.DateField(default=timezone.now, help_text="Schedule this devotional for a specific day.")
    is_featured = models.BooleanField(default=False, help_text="Mark this devotional as featured.")
    published = models.BooleanField(default=True, help_text="Control whether this devotional is publicly visible.")
    published_at = models.DateTimeField(blank=True, null=True, help_text="Timestamp when the devotional was published.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']  # Newest first

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('devotional_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        # Auto-generate the slug from the title if not provided.
        if not self.slug:
            self.slug = slugify(self.title)
            # Additional logic can be added here to ensure uniqueness if necessary.
        # Set the published_at timestamp if the devotional is published and no timestamp exists.
        if self.published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)



# SIGNALS
@receiver(pre_save, sender=VolunteerOpportunity)
def set_volunteer_opportunity_slug(sender, instance, **kwargs):
    """
    Automatically sets the slug for a volunteer opportunity before saving.
    """
    if not instance.slug:
        instance.slug = slugify(instance.title)