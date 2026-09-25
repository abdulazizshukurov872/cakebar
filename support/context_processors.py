def unread_chat(request):
    if not request.user.is_authenticated:
        return {}
    count = request.user.support_thread.filter(is_from_admin=True, read_by_customer=False).count()
    ctx = {"unread_chat_count": count}
    if request.user.is_superuser:
        from .models import ChatMessage
        ctx["unread_admin_chat_count"] = ChatMessage.objects.filter(
            is_from_admin=False, read_by_admin=False
        ).count()
    return ctx
