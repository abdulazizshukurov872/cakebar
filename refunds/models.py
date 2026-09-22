from django.conf import settings
from django.db import models
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

        self.status = "tasdiqlandi"
        self.refund_amount = amount
        self.admin_comment = admin_comment
        self.resolved_at = timezone.now()
        self.save()
        self.order.status = "qaytarildi"
        self.order.save()
        if self.order.payment_method == "naqd":
            user = self.user
            user.balance = user.balance + amount
            user.save(update_fields=["balance"])
        notify(self.user, "Qaytarish tasdiqlandi", f"Buyurtma #{self.order.id} uchun {amount:.0f} so'm qaytarildi.", link="/my-orders/")

    def reject(self, admin_comment=""):
        from notifications.services import notify

        self.status = "rad_etildi"
        self.admin_comment = admin_comment
        self.resolved_at = timezone.now()
        self.save()
        notify(self.user, "Qaytarish so'rovi rad etildi", admin_comment or "Sabab ko'rsatilmagan.", link="/my-orders/")
