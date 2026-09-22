import logging

from django.core.mail import send_mail

from .models import Notification

logger = logging.getLogger(__name__)


def notify(user, title, message, link=""):
    """Create an in-app notification and best-effort send an email.

    Email uses whatever EMAIL_BACKEND is configured (console by default,
    so nothing is lost — it just prints to the server log until real SMTP
    settings are provided via environment variables).
    """
    Notification.objects.create(user=user, title=title, message=message, link=link)

    if getattr(user, "email", ""):
        try:
            send_mail(
                subject=f"CakeBar — {title}",
                message=message,
                from_email=None,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            logger.exception("Failed to send notification email to %s", user.email)
