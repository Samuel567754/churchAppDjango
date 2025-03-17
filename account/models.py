from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from settings.fields import CompressedImageField

class Church(models.Model):
    """
    Represents a church entity.
    """
    name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    logo = CompressedImageField(upload_to='church_logos/', blank=True, null=True)  # Ensure Pillow is 
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_churches', editable=False)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_churches', editable=False)
    
    class Meta:
        verbose_name_plural = "Churches"
    
    def __str__(self):
        return self.name


# Signals
@receiver(pre_save, sender=Church)
def set_church_creator_and_updater(sender, instance, **kwargs):
    """
    Automatically populates created_by and updated_by fields based on the user.
    """
    if not instance.pk: # Check if it is a new instance
      if hasattr(instance, '_state') and hasattr(instance._state, 'adding') and instance._state.adding:
          instance.created_by = instance.updated_by = User.objects.filter(is_superuser=True).first() # User is not passed, getting a default user
    else:
        instance.updated_by = User.objects.filter(is_superuser=True).first() # User is not passed, getting a default user