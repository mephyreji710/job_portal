"""
Convenience helper to create in-app notifications.
Import and call `notify(user, notif_type, title, message='', link='')` from
any view that should fire a notification.
"""
from .models import Notification


def notify(user, notif_type, title, message='', link='', from_user=None):
    """Create a Notification record for *user*. Silently ignores errors."""
    try:
        Notification.objects.create(
            user=user,
            from_user=from_user,
            notif_type=notif_type,
            title=title,
            message=message,
            link=link,
        )
    except Exception:
        pass
