"""One-off ops helper: promote/create a superadmin from env vars.

Reads CAKEBAR_BOOTSTRAP_PHONE / CAKEBAR_BOOTSTRAP_PASSWORD (never committed
to source — set as a temporary env var on the host, removed after use) and
creates or updates that account as an active superuser/staff account.
No-ops quietly when the env vars aren't set, so it's safe to leave wired
into a build step permanently.
"""
from django.conf import settings
from django.core.management.base import BaseCommand

from accounts.models import User


class Command(BaseCommand):
    help = "Create/promote a superadmin from CAKEBAR_BOOTSTRAP_PHONE/PASSWORD env vars."

    def handle(self, *args, **options):
        phone = getattr(settings, "BOOTSTRAP_ADMIN_PHONE", "")
        password = getattr(settings, "BOOTSTRAP_ADMIN_PASSWORD", "")
        if not phone or not password:
            self.stdout.write("CAKEBAR_BOOTSTRAP_PHONE/PASSWORD not set — skipping.")
            return
        user, created = User.objects.get_or_create(
            username=phone,
            defaults={"phone": phone, "phone_verified": True},
        )
        user.phone = phone
        user.phone_verified = True
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(
            f"{'Created' if created else 'Updated'} superadmin {phone}"
        ))
