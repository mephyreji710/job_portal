from .models import Notification


def notifications_ctx(request):
    """Inject unread count + 6 recent notifications into every template."""
    if not request.user.is_authenticated:
        return {}
    qs = Notification.objects.filter(user=request.user)
    return {
        'unread_notif_count': qs.filter(is_read=False).count(),
        'recent_notifs':      qs[:6],
    }
