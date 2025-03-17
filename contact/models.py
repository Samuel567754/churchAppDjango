from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
# from membership.models import Member
from django.apps import apps
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from versatileimagefield.fields import VersatileImageField, PPOIField
from settings.fields import CompressedImageField

class ImageMixin(models.Model):
    image = CompressedImageField(
        upload_to='uploads/',
        blank=True,
        null=True,
    )
    class Meta:
        abstract = True


# Abstract Model for Social Media Links
class SocialMediaMixin(models.Model):
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)

    class Meta:
        abstract = True


# Abstract Model for Image Fields
# class ImageMixin(models.Model):
#     image = models.ImageField(upload_to='uploads/', blank=True, null=True)

#     class Meta:
#         abstract = True
        
        

# Concrete models inheriting from the abstract models
class ConcreteImageMixin(ImageMixin):
    # You can add more fields here if needed
    pass

class ConcreteSocialMediaMixin(SocialMediaMixin):
    # You can add more fields here if needed
    pass


class Staff(SocialMediaMixin, ImageMixin):
    member = models.OneToOneField('membership.Member', on_delete=models.CASCADE)
    position = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name_plural = "Staff Members"

    def __str__(self):
        return f"{self.member.user.get_full_name()} - {self.position}"




# Contact Model
# class Contact(models.Model):
#     name = models.CharField(max_length=255)
#     email = models.EmailField()
#     phone = models.CharField(max_length=20)
#     subject = models.CharField(max_length=255)
#     message = models.TextField()
#     date_sent = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         indexes = [models.Index(fields=['email', 'date_sent'])]
    
#     def __str__(self):
#         return self.subject



class Contact(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "Pending", _("Pending")
        IN_PROGRESS = "In Progress", _("In Progress")
        RESOLVED = "Resolved", _("Resolved")

    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',  # Allows +233..., 024..., etc.
                message=_("Enter a valid phone number (e.g., +233123456789 or 0241234567).")
            )
        ],
        help_text="Format: +233xxxxxxxxx or 024xxxxxxx"
    )
    subject = models.CharField(max_length=255)
    message = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=15, choices=StatusChoices.choices, default=StatusChoices.PENDING
    )
    responded = models.BooleanField(default=False, help_text="Mark as True when response is sent")

    class Meta:
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["date_sent"]),
            models.Index(fields=["status"]),
        ]
        ordering = ["-date_sent"]

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.get_status_display()})"



# NOTIFICATIONS Model
class Notification(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    # Member-specific notification (optional)
    member = models.ForeignKey(
        'membership.Member',  
        on_delete=models.SET_NULL,
        null=True,
        blank=True  # Allows NULL for general notifications
    )

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        if self.member:
            return f"Notification for {self.member.user.username} - {self.title}"
        return f"General Notification - {self.title}"

# Newsletter Subscription Model
class NewsletterSubscription(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['email'])]

    def __str__(self):
        return self.email


# NEWSLETTER Model
class Newsletter(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    recipients = models.ManyToManyField(User, blank=True)
    attachment = models.FileField(upload_to='newsletters/', blank=True, null=True)
    is_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_sent']
    
    def __str__(self):
        return self.title
    
    

#Signals
# @receiver(pre_save, sender=Staff)
# def set_staff_order(sender, instance, **kwargs):
#   if not instance.order:
#         instance.order = Staff.objects.count() + 1

@receiver(pre_save, sender=Staff)
def set_staff_order(sender, instance, **kwargs):
    if not instance.order:
        staff_model = apps.get_model('contact', 'Staff')
        instance.order = staff_model.objects.count() + 1
