from celery import shared_task
from django.core.mail import EmailMultiAlternatives, get_connection
from django.utils.timezone import localtime
from datetime import timedelta
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Q
from .models import Appointment, LiveStream
from django.utils.timezone import now
import random
from django.core.mail import send_mail
from .utils import get_bible_verse
from membership.models import Member  # adjust this import to your Member model
from contact.models import Notification
from django.db import close_old_connections

import datetime
import logging

logger = logging.getLogger(__name__)  # Set up logging

@shared_task
def send_appointment_reminders():
    
    # Close any old connections so a new one is created in this thread
    close_old_connections()
    """
    Sends email reminders to users about their upcoming appointments.
    """
    today = localtime().date()
    DAYS_AHEAD = 2  # Easily adjustable

    try:
        # Get upcoming appointments within the next 2 days that are accepted and not reminded yet
        upcoming_appointments = Appointment.objects.filter(
            date__range=[today, today + timedelta(days=DAYS_AHEAD)],
            status=Appointment.STATUS_ACCEPTED,
            is_deleted=False,
            reminder_sent=False  # Ensure we only send once per appointment
        )

        appointment_count = upcoming_appointments.count()
        print(f"[DEBUG] Found {appointment_count} upcoming appointments.")  # Debugging

        if appointment_count == 0:
            return "[DEBUG] No upcoming appointments to remind."

        emails = []
        appointment_ids = []  # Store IDs for bulk update

        for appointment in upcoming_appointments:
            member = appointment.member
            user = getattr(member, "user", None)

            if not user or not user.email:
                print(f"[WARNING] No email found for member: {member}")
                continue  # Skip if user or email is missing

            subject = "Reminder: Upcoming Appointment"
            from_email = settings.DEFAULT_FROM_EMAIL  # Use Django settings email
            recipient = user.email

            # Format date & day
            appointment_day = appointment.date.strftime('%A')  # Example: "Monday"

            # Plain text version
            text_content = (
                f"Dear {user.first_name},\n\n"
                f"This is a reminder of your appointment scheduled on {appointment.date} ({appointment_day}).\n\n"
                f"If you cannot make it, please update your response.\n\nThank you!"
            )

            # HTML version
            html_content = render_to_string(
                "worship/emails/appointment_reminder.html",
                {"user": user, "appointment": appointment},
            )

            # Create email object
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=[recipient],
            )

            # Attach HTML content
            email.attach_alternative(html_content, "text/html")

            # Add to email list for batch sending
            emails.append(email)
            
            # Collect appointment IDs for bulk update
            appointment_ids.append(appointment.id)

        # Send emails in bulk if any exist
        if emails:
            connection = get_connection()
            connection.send_messages(emails)

            # Bulk update reminder_sent status
            Appointment.objects.filter(id__in=appointment_ids).update(reminder_sent=True)

        return f"Sent {len(emails)} appointment reminders."

    except Exception as e:
        print(f"[ERROR] Failed to send appointment reminders: {e}")
        return f"[ERROR] {e}"


@shared_task
def reset_reminders():
    # Close any old connections so a new one is created in this thread
    close_old_connections()
    """
    Resets reminder_sent flag for appointments that have already passed.
    This allows reminders to be sent again if the appointment is rescheduled.
    """
    today = localtime().date()

    try:
        # Find past appointments where the reminder was sent
        past_appointments = Appointment.objects.filter(
            date__lt=today,
            reminder_sent=True
        )

        appointment_count = past_appointments.count()
        print(f"[DEBUG] Resetting reminders for {appointment_count} past appointments.")

        if appointment_count > 0:
            # Bulk update reminder_sent flag
            past_appointments.update(reminder_sent=False)

        return f"Reset {appointment_count} appointment reminders."

    except Exception as e:
        print(f"[ERROR] Failed to reset appointment reminders: {e}")
        return f"[ERROR] {e}"
    
    

@shared_task
def archive_old_appointments():
    
    # Close any old connections so a new one is created in this thread
    close_old_connections()
    """
    Archives past appointments by setting `is_archived=True` for appointments before today.
    """
    today = datetime.date.today()  # ✅ More reliable than now().date()

    # Fetch past appointments that are not archived
    past_appointments = Appointment.objects.filter(date__lt=today, is_archived=False)
    count = past_appointments.count()  # ✅ Avoid double querying

    if count > 0:
        past_appointments.update(is_archived=True)
        message = f"Archived {count} appointments"
    else:
        message = "No appointments to archive"

    logger.info(message)  # ✅ Log the task execution

    return message


@shared_task
def send_bible_verse_notification():
    
    # Close any old connections so a new one is created in this thread
    close_old_connections()
    """
    Fetch a random Bible verse from bible-api.com (using a supported translation),
    send it via email, and create a Notification instance for each member.
    """
    # Define a list of Bible references to choose from (adjust as needed)
    references = ["John 3:16", "Psalm 23:1", "Philippians 4:13"]
    reference = random.choice(references)
    
    # Choose the translation (supported: 'kjv', 'asv', 'web')
    translation = "kjv"  # Change to 'asv' or 'web' if desired
    verse = get_bible_verse(reference=reference, translation=translation)
    
    subject = "Today's Bible Verse"
    message = (
        f"Dear Member,\n\n"
        f"Here is today's Bible verse ({translation.upper()}):\n\n"
        f"{verse}\n\n"
        f"May it inspire you throughout the day.\n\n"
        f"Blessings,\nYour Church Team"
    )
    from_email = settings.DEFAULT_FROM_EMAIL

    # Get all members who have an email address
    members = Member.objects.exclude(user__email="")

    # Create a list of recipient emails for sending the email notification
    recipient_list = list(members.values_list('user__email', flat=True))
    
    if recipient_list:
        # Send the email notification to all members
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        
        # Create a Notification instance for each member
        for member in members:
            Notification.objects.create(
                title="Today's Bible Verse",
                content=verse,  # You can customize this further if desired
                member=member,  # Link the notification to the member
            )# tasks.py

@shared_task
def update_live_stream_status():
    now = timezone.now()
    # Mark streams as live if the scheduled time is reached and within 1 hour
    live_streams = LiveStream.objects.all()
    for stream in live_streams:
        stream_start = stream.scheduled_time
        stream_end = stream_start + timedelta(hours=1)  # Assuming 1-hour duration
        if stream_start <= now < stream_end:
            if not stream.is_live:
                stream.is_live = True
                stream.save(update_fields=['is_live'])
        else:
            if stream.is_live:
                stream.is_live = False
                stream.save(update_fields=['is_live'])

            
            















# from celery import shared_task
# from django.core.mail import EmailMultiAlternatives, get_connection
# from django.utils.timezone import localtime, now
# from datetime import timedelta
# from django.template.loader import render_to_string
# from django.conf import settings
# from .models import Appointment
# from django.db.models import Q

# @shared_task
# def send_appointment_reminders():
#     """
#     Sends email reminders to users about their upcoming appointments.
#     """
#     today = localtime().date()

#     # Get upcoming appointments within the next 2 days that are accepted
    
#     DAYS_AHEAD = 2  # Easily adjustable
#     upcoming_appointments = Appointment.objects.filter(
#         Q(date__gte=today, date__lte=today + timedelta(days=DAYS_AHEAD)),
#         status=Appointment.STATUS_ACCEPTED,
#         is_deleted=False,
#         reminder_sent=False  # Ensure we only send once per appointment
        
#     )
#     # upcoming_appointments = Appointment.objects.filter(
#     #     date__range=[today, today + timedelta(days=2)],
#     #     status=Appointment.STATUS_ACCEPTED,
#     #     is_deleted=False  # Exclude soft-deleted appointments
#     # )

#     appointment_count = upcoming_appointments.count()
#     print(f"[DEBUG] Found {appointment_count} upcoming appointments.")  # Debugging

#     if appointment_count == 0:
#         return "[DEBUG] No upcoming appointments to remind."

#     emails = []
    
#     for appointment in upcoming_appointments:
#         member = appointment.member
#         user = getattr(member, "user", None)

#         if not user or not user.email:
#             print(f"[WARNING] No email found for member: {member}")
#             continue  # Skip if user or email is missing

#         subject = "Reminder: Upcoming Appointment"
#         from_email = settings.DEFAULT_FROM_EMAIL  # Use Django settings email
#         recipient = user.email

#         # Format date & day
#         appointment_day = appointment.date.strftime('%A')  # Example: "Monday"

#         # Plain text version
#         text_content = (
#             f"Dear {user.first_name},\n\n"
#             f"This is a reminder of your appointment scheduled on {appointment.date} ({appointment_day}).\n\n"
#             f"If you cannot make it, please update your response.\n\nThank you!"
#         )

#         # HTML version
#         html_content = render_to_string(
#             "worship/emails/appointment_reminder.html",
#             {"user": user, "appointment": appointment},
#         )

#         # Create email object
#         email = EmailMultiAlternatives(
#             subject=subject,
#             body=text_content,
#             from_email=from_email,
#             to=[recipient],
#         )

#         # Attach HTML content
#         email.attach_alternative(html_content, "text/html")

#         # Add to email list for batch sending
#         emails.append(email)
        
#          # Mark the appointment as reminded
#         appointment.reminder_sent = True
#         appointment.save()

#     # Send emails in bulk if any exist
#     if emails:
#         connection = get_connection()
#         connection.send_messages(emails)

#     return f"Sent {len(emails)} appointment reminders."





# "appointment.reschedule_link": f"https://yourdomain.com/appointments/{appointment.id}/reschedule/",
#         "appointment.cancel_link": f"https://yourdomain.com/appointments/{appointment.id}/cancel/",



# from celery.schedules import crontab
# from celery import Celery
# from .tasks import send_appointment_reminders

# app = Celery("your_project")

# # Schedule the task to run every day at 8 AM
# app.conf.beat_schedule = {
#     "send-reminders-every-morning": {
#         "task": "appointments.tasks.send_appointment_reminders",
#         "schedule": crontab(hour=8, minute=0),
#     }
# }