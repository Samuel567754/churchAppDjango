import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import requests

logger = logging.getLogger(__name__)  # Set up logging

def get_bible_verse(reference="John 3:16", translation="kjv"):
    """
    Fetches a Bible verse from bible-api.com.
    
    Parameters:
        reference (str): Bible reference, e.g. "John 3:16".
        translation (str): Translation to use (supported: 'kjv', 'asv', 'web').
    
    Returns:
        str: A string combining the reference and the verse text, or an error message.
    """
    url = f"https://bible-api.com/{reference}?translation={translation}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return f"{data.get('reference')} - {data.get('text')}"
        else:
            return "Verse not available."
    except Exception:
        return "Verse not available."


def send_email_notification(appointment):
    """
    Sends an email notification to the appointed member about their appointment.
    
    Args:
        appointment (Appointment): The appointment instance containing member and role details.
    
    Returns:
        bool: True if email was sent successfully, False otherwise.
    """
    try:
        recipient_email = appointment.member.user.email
        if not recipient_email:
            logger.warning(f"Appointment for {appointment.member} has no email. Skipping.")
            return False  # Skip if no email

        subject = "⛪ Church Appointment Notification"
        context = {
            'member_name': appointment.member.user.get_full_name(),
            'role': appointment.role.name,
            'day': appointment.day.name,
            'date': appointment.date,
        }

        html_content = render_to_string("worship/emails/appointment_email.html", context)
        text_content = strip_tags(html_content)  # Convert HTML to plain text

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email="admin@yourchurch.com",
            to=[recipient_email]
        )
        email.attach_alternative(html_content, "text/html")  # Attach HTML version
        email.send()

        logger.info(f"Email sent successfully to {recipient_email}.")
        return True

    except Exception as e:
        logger.error(f"Error sending email to {recipient_email}: {e}")
        return False
