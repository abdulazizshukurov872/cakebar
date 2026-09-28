"""Pre-demo cleanup: deletes every account except the whitelisted admin
phone(s). Destructive on purpose — cascades to that user's orders,
favorites, reviews, addresses, refund requests and chat messages
(all CASCADE per their FKs). Run once, then remove from buildCommand."""
from django.core.management.base import BaseCommand

from accounts.models import User

KEEP_PHONES = {"+998900986121"}


class Command(BaseCommand):
    help = "Deletes every user except KEEP_PHONES. Destructive — for pre-demo cleanup only."

    def handle(self, *args, **options):
        qs = User.objects.exclude(username__in=KEEP_PHONES).exclude(phone__in=KEEP_PHONES)
        count = qs.count()
        qs.delete()
        remaining = User.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"Deleted {count} user(s). {remaining} remain (kept: {', '.join(KEEP_PHONES)})."
        ))
