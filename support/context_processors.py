def unread_chat(request):
    if not request.user.is_authenticated:
        return {}
    count = request.user.support_thread.filter(is_from_admin=True, read_by_customer=False).count()
    return {"unread_chat_count": count}
