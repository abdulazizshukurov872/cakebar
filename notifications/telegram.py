"""Telegram Bot API: customer notifications, admin alerts and Mini App login.

Only active once CAKEBAR_TELEGRAM_BOT_TOKEN is set. Users link their
account from their profile page: they DM the bot "/start <code>" and the
webhook below binds their chat id to that account. After that, opening the
shop from the bot's "Do'kon" button (a Telegram Mini App) logs them in
automatically.
"""
import hashlib
import hmac
import json
import logging
import time
from urllib.parse import parse_qsl

import requests
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

logger = logging.getLogger(__name__)

API_BASE = "https://api.telegram.org/bot{token}/{method}"
INIT_DATA_MAX_AGE = 24 * 60 * 60


def is_configured():
    return bool(settings.TELEGRAM_BOT_TOKEN)


def webhook_secret():
    """Explicit secret if set, otherwise one derived from the bot token —
    never a guessable constant."""
    if settings.TELEGRAM_WEBHOOK_SECRET:
        return settings.TELEGRAM_WEBHOOK_SECRET
    return hashlib.sha256(f"webhook:{settings.TELEGRAM_BOT_TOKEN}".encode()).hexdigest()[:32]


def mini_app_url():
    if not settings.SITE_URL.startswith("https://"):
        return ""  # Telegram only opens Mini Apps over HTTPS.
    return settings.SITE_URL.rstrip("/") + "/tg/"


def send_message(chat_id, text, reply_markup=None):
    if not is_configured() or not chat_id:
        return
    url = API_BASE.format(token=settings.TELEGRAM_BOT_TOKEN, method="sendMessage")
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload, timeout=5)
    except requests.RequestException:
        logger.exception("Failed to send Telegram message to chat %s", chat_id)


def _shop_button():
    url = mini_app_url()
    if not url:
        return None
    return {"inline_keyboard": [[{"text": "🍰 Do'konni ochish", "web_app": {"url": url}}]]}


def notify_admins(text):
    """Post to the staff group/chat (CAKEBAR_TELEGRAM_ADMIN_CHAT_ID) in the background."""
    if not (is_configured() and settings.TELEGRAM_ADMIN_CHAT_ID):
        return
    from .services import run_in_background

    run_in_background(send_message, settings.TELEGRAM_ADMIN_CHAT_ID, text)


def handle_update(update):
    """Shared handler for one Telegram update — used by both the webhook
    (production, needs a public HTTPS URL) and the local polling command
    (dev, works behind localhost via getUpdates).
    """
    message = update.get("message") or {}
    text = (message.get("text") or "").strip()
    chat = message.get("chat") or {}
    chat_id = chat.get("id")

    if text.startswith("/start") and chat_id:
        from accounts.models import User

        parts = text.split(maxsplit=1)
        code = parts[1].strip().upper() if len(parts) > 1 else ""
        user = User.objects.filter(telegram_link_code=code).first() if code else None
        if user:
            from accounts.models import generate_telegram_link_code

            # One chat = one account (the Mini App logs this chat in as that
            # account), and the code is single-use so a leaked one can't be
            # used later to take over the login.
            User.objects.filter(telegram_chat_id=str(chat_id)).exclude(pk=user.pk).update(telegram_chat_id="")
            user.telegram_chat_id = str(chat_id)
            user.telegram_link_code = generate_telegram_link_code()
            user.save(update_fields=["telegram_chat_id", "telegram_link_code"])
            send_message(
                chat_id,
                "CakeBar hisobingiz ulandi! Endi buyurtma holati haqida shu yerga xabar beramiz.",
                reply_markup=_shop_button(),
            )
        elif not code and User.objects.filter(telegram_chat_id=str(chat_id)).exists():
            send_message(chat_id, "Xush kelibsiz! Do'konni pastdagi tugma orqali oching.", reply_markup=_shop_button())
        else:
            send_message(chat_id, "Kod topilmadi. Profilingizdagi kodni to'g'ri yuboring: /start KOD")
    elif text == "/shop" and chat_id:
        button = _shop_button()
        send_message(chat_id, "CakeBar do'koni:" if button else "Do'kon hozircha faqat saytda ishlaydi.", reply_markup=button)


def verify_init_data(init_data):
    """Validate Telegram Mini App initData (per core.telegram.org/bots/webapps
    "Validating data received via the Mini App"). Returns the Telegram user
    dict, or None if the signature is wrong or the data is stale."""
    if not (is_configured() and init_data):
        return None
    fields = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = fields.pop("hash", "")
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(fields.items()))
    secret_key = hmac.new(b"WebAppData", settings.TELEGRAM_BOT_TOKEN.encode(), hashlib.sha256).digest()
    expected = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, received_hash):
        return None
    try:
        if time.time() - int(fields.get("auth_date", "0")) > INIT_DATA_MAX_AGE:
            return None
        return json.loads(fields.get("user", "{}")) or None
    except (ValueError, TypeError):
        return None


@csrf_exempt
@require_POST
def webhook(request, secret):
    if not is_configured():
        return HttpResponse(status=503)
    if not hmac.compare_digest(secret, webhook_secret()):
        return HttpResponseForbidden()

    try:
        update = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    handle_update(update)
    return HttpResponse("ok")
