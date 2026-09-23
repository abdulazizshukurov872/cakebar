import logging
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction

from . import eskiz, telegram
from .models import Notification

logger = logging.getLogger(__name__)

# External channels (SMTP, Eskiz, Telegram) can each take seconds; sending
# them from a small background pool keeps checkout and admin saves fast.
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="notify")


def notify(user, title, message, link=""):
    """Create an in-app notification and best-effort send it via email, SMS
    and Telegram — each channel is used only if it's actually configured
    (see settings.py), so nothing breaks when it isn't.
    """
    Notification.objects.create(user=user, title=title, message=message, link=link)

    # Capture plain values now: the worker thread must not touch the ORM.
    email = getattr(user, "email", "")
    phone = getattr(user, "phone", "")
    chat_id = getattr(user, "telegram_chat_id", "")

    def deliver():
        if settings.NOTIFY_ASYNC:
            _executor.submit(_send_external, title, message, email, phone, chat_id)
        else:
            _send_external(title, message, email, phone, chat_id)

    # Only send once the surrounding transaction (if any) has committed, so
    # nobody gets told about an order that was rolled back.
    transaction.on_commit(deliver)


def _send_external(title, message, email, phone, chat_id):
    if email:
        try:
            send_mail(
                subject=f"CakeBar — {title}",
                message=message,
                from_email=None,
                recipient_list=[email],
                fail_silently=True,
            )
        except Exception:
            logger.exception("Failed to send notification email to %s", email)

    if phone and eskiz.is_configured():
        try:
            eskiz.send_sms(phone, f"CakeBar: {title} — {message}")
        except Exception:
            logger.exception("Failed to send notification SMS to %s", phone)

    if chat_id and telegram.is_configured():
        try:
            telegram.send_message(chat_id, f"CakeBar\n{title}\n{message}")
        except Exception:
            logger.exception("Failed to send Telegram notification to chat %s", chat_id)


def run_in_background(func, *args):
    """Fire-and-forget helper for other slow side effects (e.g. admin alerts)."""
    def deliver():
        if settings.NOTIFY_ASYNC:
            _executor.submit(func, *args)
        else:
            func(*args)
    transaction.on_commit(deliver)
