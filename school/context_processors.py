from .models import Notification


def notifications(request):
    """Make unread notifications available on every page (used by base.html)."""
    if not request.user.is_authenticated:
        return {}
    unread = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    return {
        'unread_notification': unread,
        'unread_notification_count': unread.count(),
    }
