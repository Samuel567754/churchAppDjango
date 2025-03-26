from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from membership.models import Member, Membership, Member
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

# Signal to create or update Member when Membership is created
@receiver(post_save, sender=Membership)
def create_or_update_member(sender, instance, created, update_fields, **kwargs):
    """Ensure a Member instance is created or updated when a Membership is added."""
    if created:
        Member.objects.update_or_create(
            user=instance.member.user,
            defaults={
                'date_joined': instance.join_date,
            }
        )
    elif not update_fields or 'join_date' not in update_fields:
        Member.objects.update_or_create(
            user=instance.member.user,
            defaults={
                'date_joined': instance.join_date,
            }
        )

# # Signal to create or update Membership when Member is created
# @receiver(post_save, sender=Member)
# def create_or_update_membership(sender, instance, created, update_fields, **kwargs):
#     """Ensure a Membership instance is created or updated when a Member is added."""
#     if created:
#         Membership.objects.update_or_create(
#             member=instance,
#             defaults={
#                 'join_date': instance.date_joined,
#                 'membership_type': 'regular',  # Default membership type (using the key from choices)
#             }
#         )
#     elif not update_fields or 'date_joined' not in update_fields:
#         Membership.objects.update_or_create(
#             member=instance,
#             defaults={
#                 'join_date': instance.date_joined,
#                 'membership_type': 'regular',
#             }
#         )

# Signal to create or update Membership when Member is created (only if approved)
@receiver(post_save, sender=Member)
def create_or_update_membership(sender, instance, created, update_fields, **kwargs):
    """Ensure a Membership instance is created or updated when a Member is added, 
    but only if the approval_status is 'approved'."""
    if created:
        if instance.approval_status == 'approved':  # Check if the approval_status is 'approved'
            Membership.objects.update_or_create(
                member=instance,
                defaults={
                    'join_date': instance.date_joined,
                    'membership_type': 'regular',  # Default membership type (using the key from choices)
                }
            )
    elif not update_fields or 'date_joined' not in update_fields:
        if instance.approval_status == 'approved':  # Only update membership if approved
            Membership.objects.update_or_create(
                member=instance,
                defaults={
                    'join_date': instance.date_joined,
                    'membership_type': 'regular',
                }
            )
            
        # elif instance.approval_status == 'rejected':  
        #     # Delete membership if status changes to rejected
        #     Membership.objects.filter(member=instance).delete()

# Dictionary to store previous approval_status
# previous_statuses = {}

# @receiver(pre_save, sender=Member)
# def track_previous_status(sender, instance, **kwargs):
#     """Store the previous approval_status before the Member is updated."""
#     if instance.pk:  # Ensure it's an existing record, not a new one
#         try:
#             previous_statuses[instance.pk] = Member.objects.get(pk=instance.pk).approval_status
#         except Member.DoesNotExist:
#             previous_statuses[instance.pk] = None  # Handle edge cases where the record doesn't exist

# @receiver(post_save, sender=Member)
# def create_or_update_membership(sender, instance, created, **kwargs):
#     """
#     Ensure a Membership instance is created or updated when a Member is added,
#     but only if the approval_status is 'approved'.
#     If a previously approved member is later rejected, delete their Membership.
#     """
#     if created:
#         if instance.approval_status == 'approved':  
#             Membership.objects.update_or_create(
#                 member=instance,
#                 defaults={
#                     'join_date': instance.date_joined,
#                     'membership_type': 'regular',
#                 }
#             )
#     else:
#         # Get the previous status from our dictionary
#         previous_status = previous_statuses.get(instance.pk, None)
        
#         if previous_status == 'approved' and instance.approval_status == 'rejected':
#             # If previously approved and now rejected, delete Membership
#             Membership.objects.filter(member=instance).delete()
        
#         elif instance.approval_status == 'approved':  
#             # If approved (new or existing), create/update Membership
#             Membership.objects.update_or_create(
#                 member=instance,
#                 defaults={
#                     'join_date': instance.date_joined,
#                     'membership_type': 'regular',
#                 }
#             )
    
#     # Clean up previous_statuses to prevent memory leaks
#     previous_statuses.pop(instance.pk, None)




# Delete Member when Membership is deleted
@receiver(post_delete, sender=Membership)
def delete_member_on_membership_delete(sender, instance, **kwargs):
    """Delete the associated Member when a Membership is deleted."""
    try:
        member = Member.objects.get(user=instance.member.user)
        member.delete()
    except Member.DoesNotExist:
        pass  # No Member to delete

# Delete Membership when Member is deleted
@receiver(post_delete, sender=Member)
def delete_membership_on_member_delete(sender, instance, **kwargs):
    """Delete the associated Membership when a Member is deleted."""
    try:
        membership = Membership.objects.get(member=instance)
        membership.delete()
    except Membership.DoesNotExist:
        pass  # No Membership to delete



# @receiver(post_save, sender=Member)
# def send_approval_rejection_email(sender, instance, created, **kwargs):
#     if not created:  # Only trigger when updating, not creating
#         # Check if the approval_status field has been set to a value other than 'pending'
#         if instance.approval_status != 'pending':  # Ensure approval_status is either 'approved' or 'rejected'
#             if instance.approval_status == 'approved':
#                 send_email_approved(instance.user)
#             elif instance.approval_status == 'rejected':
#                 send_email_rejected(instance.user)

# def send_email_approved(user):
#     """Send approval email to user."""
#     subject = 'Your Membership has been Approved'
#     message = render_to_string('membership/emails/member_approval_email.html', {'user': user})
#     send_mail(
#         subject, 
#         message, 
#         settings.DEFAULT_FROM_EMAIL, 
#         [user.email], 
#         fail_silently=False
#     )

# def send_email_rejected(user):
#     """Send rejection email to user."""
#     subject = 'Your Membership Application has been Rejected'
#     message = render_to_string('membership/emails/member_rejection_email.html', {'user': user})
#     send_mail(
#         subject, 
#         message, 
#         settings.DEFAULT_FROM_EMAIL, 
#         [user.email], 
#         fail_silently=False
#     )



@receiver(pre_save, sender=Member)
def detect_status_change(sender, instance, **kwargs):
    # Only check if the instance exists already (i.e. update, not create)
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            return
        # Compare the old approval_status to the new one
        if old_instance.approval_status != instance.approval_status:
            instance._status_changed = True

@receiver(post_save, sender=Member)
def send_approval_rejection_email(sender, instance, created, **kwargs):
    # Only trigger on updates, and only if the status has changed
    if not created and getattr(instance, '_status_changed', False):
        # Only send email if the new status is not 'pending'
        if instance.approval_status != 'pending':
            if instance.approval_status == 'approved':
                send_email_approved(instance.user)
            elif instance.approval_status == 'rejected':
                send_email_rejected(instance.user)


# @receiver(post_save, sender=Member)
# def send_approval_rejection_email(sender, instance, created, **kwargs):
#     if not created:  # Only trigger when updating, not creating
#         # Check if the approval_status field has been set to a value other than 'pending'
#         if instance.approval_status != 'pending':  # Ensure approval_status is either 'approved' or 'rejected'
#             if instance.approval_status == 'approved':
#                 send_email_approved(instance.user)
#             elif instance.approval_status == 'rejected':
#                 send_email_rejected(instance.user)

def send_email_approved(user):
    """Send approval email to user."""
    subject = 'Your Membership has been Approved'
    from_email = settings.DEFAULT_FROM_EMAIL  # Ensure this is set in settings.py
    
    context = {
        'user': user,
        'domain': settings.SITE_DOMAIN,
        'local': settings.LOCAL_DOMAIN,
    }

    # Render the HTML email
    html_content = render_to_string('account/emails/member_approval_email.html', context)

    # Create email with plain text fallback
    email = EmailMultiAlternatives(subject, strip_tags(html_content), from_email, [user.email])
    email.attach_alternative(html_content, "text/html")  # Attach HTML version

    email.send(fail_silently=False)

def send_email_rejected(user):
    """Send rejection email to user."""
    subject = 'Your Membership Application has been Rejected'
    from_email = settings.DEFAULT_FROM_EMAIL  # Ensure this is set in settings.py
    
    context = {
        'user': user,
        'domain': settings.SITE_DOMAIN,
        'local': settings.LOCAL_DOMAIN,
    }

    # Render the HTML email
    html_content = render_to_string('account/emails/member_rejection_email.html', context)

    # Create email with plain text fallback
    email = EmailMultiAlternatives(subject, strip_tags(html_content), from_email, [user.email])
    email.attach_alternative(html_content, "text/html")  # Attach HTML version

    email.send(fail_silently=False)







