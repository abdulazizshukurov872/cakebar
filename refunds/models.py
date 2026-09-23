from decimal import Decimal

from django.conf import settings
from django.db import models, transaction
from django.db.models import F
from django.utils import timezone

from orders.models import Order


class RefundRequest(models.Model):
    REASON_CHOICES = [
        ("tami", "Ta'mi yoqmadi"),
        ("buzilgan", "Mahsulot buzilgan/sifatsiz yetib keldi"),
        ("notogri", "Noto'g'ri mahsulot yuborildi"),
        ("muddati", "Muddati o'tgan"),
        ("boshqa", "Boshqa sabab"),
    ]
    STATUS_CHOICES = [
        ("kutilmoqda", "Kutilmoqda"),
        ("tasdiqlandi", "Tasdiqlandi"),
        ("rad_etildi", "Rad etildi"),
    ]

    order = models.OneToOneField(Order, verbose_name="Buyurtma", related_name="refund_request", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Foydalanuvchi", related_name="refund_requests", on_delete=models.CASCADE)
    reason = models.CharField("Sabab", max_length=20, choices=REASON_CHOICES)
    comment = models.TextField("Izoh", blank=True)
    image = models.ImageField("Dalil rasm", upload_to="refunds/", null=True, blank=True)
    status = models.CharField("Status", max_length=20, choices=STATUS_CHOICES, default="kutilmoqda")
    refund_amount = models.DecimalField("Qaytarilgan summa", max_digits=12, decimal_places=0, default=0)
    admin_comment = models.TextField("Admin izohi", blank=True)
    requested_at = models.DateTimeField("So'rov sanasi", auto_now_add=True)
    resolved_at = models.DateTimeField("Hal qilingan sana", null=True, blank=True)

    class Meta:
        verbose_name = "Qaytarish so'rovi"
        verbose_name_plural = "Qaytarish so'rovlari"
        ordering = ["-requested_at"]

    def __str__(self):
        return f"Refund #{self.pk} — {self.order}"

    def approve(self, amount, admin_comment=""):
        from notifications.services import notify

        from accounts.models import User

        amount = min(Decimal(amount), self.order.total_amount)
        with transaction.atomic():
            # The status filter makes a second approve (double click, bulk
            # action on an already-approved row) a no-op instead of paying twice.
            claimed = RefundRequest.objects.filter(pk=self.pk, status="kutilmoqda").update(
                status="tasdiqlandi", refund_amount=amount,
                admin_comment=admin_comment, resolved_at=timezone.now(),
            )
            if not claimed:
                return False
            self.refresh_from_db()
            self.order.status = "qaytarildi"
            self.order.save()
            # Money goes back to the wallet whatever the original payment
            # method was; loyalty points earned on this order are taken back
            # (as many as the customer still has).
            user = User.objects.select_for_update().get(pk=self.user_id)
            points_back = min(self.order.points_earned, user.loyalty_points)
            User.objects.filter(pk=user.pk).update(
                balance=F("balance") + amount,
                loyalty_points=F("loyalty_points") - points_back,
            )
        notify(
            self.user, "Qaytarish tasdiqlandi",
            f"Buyurtma #{self.order.id} uchun {amount:.0f} so'm wallet balansingizga qaytarildi.",
            link="/my-orders/",
        )
        return True

    def reject(self, admin_comment=""):
        from notifications.services import notify

        claimed = RefundRequest.objects.filter(pk=self.pk, status="kutilmoqda").update(
            status="rad_etildi", admin_comment=admin_comment, resolved_at=timezone.now(),
        )
        if not claimed:
            return False
        self.refresh_from_db()
        notify(self.user, "Qaytarish so'rovi rad etildi", admin_comment or "Sabab ko'rsatilmagan.", link="/my-orders/")
        return True
