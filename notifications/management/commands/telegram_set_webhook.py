import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.urls import reverse

from notifications.telegram import API_BASE, is_configured, mini_app_url, webhook_secret


class Command(BaseCommand):
    help = (
        "Points the Telegram bot at this site's webhook (production) and adds "
        "the 'Do'kon' Mini App button to the bot's menu. Needs CAKEBAR_SITE_URL "
        "to be the public https:// address."
    )

    def handle(self, *args, **options):
        if not is_configured():
            raise CommandError("CAKEBAR_TELEGRAM_BOT_TOKEN is not set.")
        if not settings.SITE_URL.startswith("https://"):
            raise CommandError("CAKEBAR_SITE_URL must be the public https:// URL of the site.")

        def call(method, payload):
            resp = requests.post(API_BASE.format(token=settings.TELEGRAM_BOT_TOKEN, method=method), json=payload, timeout=10)
            data = resp.json()
            if not data.get("ok"):
                raise CommandError(f"{method} failed: {data}")

        hook_url = settings.SITE_URL.rstrip("/") + reverse("telegram_webhook", args=[webhook_secret()])
        call("setWebhook", {"url": hook_url, "allowed_updates": ["message"]})
        call("setChatMenuButton", {"menu_button": {"type": "web_app", "text": "Do'kon", "web_app": {"url": mini_app_url()}}})
        self.stdout.write(self.style.SUCCESS("Webhook and Mini App menu button are set."))
