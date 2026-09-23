import time

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from notifications.telegram import API_BASE, handle_update, is_configured


class Command(BaseCommand):
    help = (
        "Long-polls Telegram for updates and processes them locally — use this "
        "during development instead of a webhook, since a webhook needs a "
        "public HTTPS URL that localhost doesn't have."
    )

    def handle(self, *args, **options):
        if not is_configured():
            self.stderr.write("CAKEBAR_TELEGRAM_BOT_TOKEN is not set — nothing to poll.")
            return

        me = requests.get(API_BASE.format(token=settings.TELEGRAM_BOT_TOKEN, method="getMe"), timeout=10).json()
        username = me.get("result", {}).get("username", "?")
        self.stdout.write(self.style.SUCCESS(f"Listening for messages to @{username}... (Ctrl+C to stop)"))

        offset = None
        while True:
            try:
                params = {"timeout": 25}
                if offset is not None:
                    params["offset"] = offset
                resp = requests.get(
                    API_BASE.format(token=settings.TELEGRAM_BOT_TOKEN, method="getUpdates"),
                    params=params, timeout=30,
                )
                resp.raise_for_status()
                updates = resp.json().get("result", [])
                for update in updates:
                    offset = update["update_id"] + 1
                    handle_update(update)
                    chat = (update.get("message") or {}).get("chat") or {}
                    self.stdout.write(f"handled update from chat {chat.get('id')}")
            except requests.RequestException as exc:
                self.stderr.write(f"Telegram poll error: {exc}")
                time.sleep(5)
            except KeyboardInterrupt:
                break
