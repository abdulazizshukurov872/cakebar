from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Max, Q, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from accounts.models import User
from notifications import telegram
from notifications.services import notify

from .models import ChatMessage

staff_required = user_passes_test(lambda u: u.is_active and u.is_superuser, login_url="login")


@login_required
def customer_chat(request):
    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        if text:
            ChatMessage.objects.create(
                customer=request.user, sender=request.user, is_from_admin=False,
                text=text[:2000], read_by_customer=True, read_by_admin=False,
            )
            telegram.notify_admins(
                f"💬 Yangi xabar ({request.user.phone or request.user.username}):\n{text[:300]}"
            )
            messages.success(request, "Xabaringiz yuborildi. Administrator 24 soat ichida ko'rib chiqadi.")
        return redirect("customer_chat")

    ChatMessage.objects.filter(customer=request.user, is_from_admin=True, read_by_customer=False) \
        .update(read_by_customer=True)
    messages_qs = ChatMessage.objects.filter(customer=request.user).select_related("sender")
    return render(request, "support/customer_chat.html", {"chat_messages": messages_qs, "active": "chat"})


@staff_required
def admin_chat_list(request):
    threads = (
        User.objects.filter(support_thread__isnull=False)
        .annotate(
            last_at=Max("support_thread__created_at"),
            unread=Count("support_thread", filter=Q(support_thread__is_from_admin=False, support_thread__read_by_admin=False)),
        )
        .order_by("-unread", "-last_at")
        .distinct()
    )
    return render(request, "support/admin_chat_list.html", {"threads": threads})


@staff_required
def admin_chat_detail(request, user_id):
    customer = get_object_or_404(User, pk=user_id)

    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        if text:
            ChatMessage.objects.create(
                customer=customer, sender=request.user, is_from_admin=True,
                text=text[:2000], read_by_admin=True, read_by_customer=False,
            )
            notify(customer, "Admindan javob keldi", text[:150], link=reverse("customer_chat"))
        return redirect("admin_chat_detail", user_id=user_id)

    ChatMessage.objects.filter(customer=customer, is_from_admin=False, read_by_admin=False) \
        .update(read_by_admin=True)
    messages_qs = ChatMessage.objects.filter(customer=customer).select_related("sender")
    return render(request, "support/admin_chat_detail.html", {"customer": customer, "chat_messages": messages_qs})
