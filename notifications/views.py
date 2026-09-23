from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from . import telegram
from .models import Notification


@login_required
def notification_list(request):
    notifications = request.user.notifications.all()
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, "notifications/list.html", {"notifications": notifications})


@login_required
@require_POST
def notification_open(request, pk):
    n = get_object_or_404(Notification, pk=pk, user=request.user)
    n.is_read = True
    n.save(update_fields=["is_read"])
    return redirect(n.link or "notification_list")


def mini_app(request):
    """Entry page for the Telegram Mini App: its JS posts Telegram's signed
    initData to mini_app_auth and then continues to the shop."""
    return render(request, "notifications/mini_app.html")


@require_POST
def mini_app_auth(request):
    from accounts.models import User

    tg_user = telegram.verify_init_data(request.POST.get("init_data", ""))
    if not tg_user or "id" not in tg_user:
        return JsonResponse({"ok": False, "message": "Telegram ma'lumotlari tasdiqlanmadi."}, status=403)

    user = User.objects.filter(telegram_chat_id=str(tg_user["id"]), is_active=True).first()
    if user is None:
        # Not linked yet: they can still browse; linking is done from the profile page.
        return JsonResponse({
            "ok": True, "linked": False, "redirect": reverse("product_list"),
            "message": "Hisobingiz hali ulanmagan. Saytga kirib, profilingizdagi /start kodini botga yuboring.",
        })
    if request.user != user:
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return JsonResponse({"ok": True, "linked": True, "redirect": reverse("product_list")})
