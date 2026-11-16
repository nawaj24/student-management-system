from .models import Notification


def create_notification(user, message):
    """Save a notification for the logged-in user (shown in the bell icon)."""
    if user.is_authenticated:
        Notification.objects.create(user=user, message=message)
