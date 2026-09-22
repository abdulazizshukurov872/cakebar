def notifications(request):
    if not request.user.is_authenticated:
        return {}
    qs = request.user.notifications.all()
    return {
        "unread_notifications_count": qs.filter(is_read=False).count(),
        "recent_notifications": qs[:6],
    }
