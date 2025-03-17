from django.db.models.signals import post_save
from django.dispatch import receiver
from membership.models import Member
from .models import MemberSettings  # Import MemberSettings

@receiver(post_save, sender=Member)
def create_member_settings(sender, instance, created, **kwargs):
    """
    Automatically creates default settings for a new church member.
    """
    if created:
        MemberSettings.objects.create(member=instance)
