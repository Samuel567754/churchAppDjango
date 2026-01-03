from .models import Member  # Import your Member model
from contact.models import Notification  # Import the Notification model

def member_profile(request):
    """Make the logged-in member's profile available globally"""
    user = getattr(request, 'user', None)
    if user and user.is_authenticated and hasattr(user, 'member'):
        return {'member': user.member}  # Provide member to templates
    return {}  # Return an empty dictionary if not logged in


def notification_context(request):
    user = getattr(request, 'user', None)
    if user and user.is_authenticated:
        # Get member object associated with the user
        member = getattr(user, 'member', None)
        
        # Get notifications: both general and user-specific
        notifications = Notification.objects.filter(member__isnull=True)  # General notifications
        if member:
            user_notifications = Notification.objects.filter(member=member)  # Personal notifications
            notifications = notifications | user_notifications  # Combine both

        notifications = notifications.order_by('-created_at')  # Ensure latest notifications come first
        unread_count = notifications.filter(is_read=False).count()
    else:
        notifications = []
        unread_count = 0

    return {
        'notifications': notifications,
        'unread_notification_count': unread_count
    }
