from django.conf import settings
from django.db import models
from django.utils import timezone

from catalog.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ("yangi", "Yangi"),
        ("tasdiqlangan", "Tasdiqlangan"),
        ("tayyorlanmoqda", "Tayyorlanmoqda"),
        ("yetkazilmoqda", "Yetkazilmoqda"),
        ("yetkazildi", "Yetkazildi"),
        ("qaytarildi", "Qaytarildi"),
        ("bekor", "Bekor qilindi"),
    ]
    PAYMENT_CHOICES = [
        ("naqd", "Naqd pul"),
        ("karta", "Karta (Payme/Click)"),
        ("wallet", "Wallet balansidan"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Foydalanuvchi", related_name="orders", on_delete=models.CASCADE)
    address = models.CharField("Yetkazib berish manzili", max_length=255)
    payment_method = models.CharField("To'lov usuli", max_length=10, choices=PAYMENT_CHOICES, default="naqd")
    status = models.CharField("Status", max_length=20, choices=STATUS_CHOICES, default="yangi")
    total_amount = models.DecimalField("Umumiy summa", max_digits=12, decimal_places=0, default=0)
    promo_code = models.CharField("Promo-kod", max_length=32, blank=True)
    discount_amount = models.DecimalField("Chegirma summasi", max_digits=12, decimal_places=0, default=0)
    created_at = models.DateTimeField("Yaratilgan sana", auto_now_add=True)
    delivered_at = models.DateTimeField("Yetkazilgan sana", null=True, blank=True)
    estimated_delivery_at = models.DateTimeField("Taxminiy yetkazish vaqti", null=True, blank=True)
    courier_name = models.CharField("Kuryer ismi", max_length=100, blank=True)
    courier_phone = models.CharField("Kuryer telefoni", max_length=32, blank=True)

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Buyurtma #{self.pk} — {self.user}"

    DEFAULT_COURIERS = [
        ("Aziz Rahimov", "+998 90 111 22 33"),
        ("Javlon Karimov", "+998 91 222 33 44"),
        ("Sardor Yusupov", "+998 93 333 44 55"),
    ]

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        old_status = None
        if not is_new:
            old_status = Order.objects.filter(pk=self.pk).values_list("status", flat=True).first()

        if not self.estimated_delivery_at and self.status != "bekor":
            self.estimated_delivery_at = (self.created_at or timezone.now()) + timezone.timedelta(hours=2)
        if self.status in ("tasdiqlangan", "tayyorlanmoqda", "yetkazilmoqda", "yetkazildi") and not self.courier_name:
            self.courier_name, self.courier_phone = self.DEFAULT_COURIERS[self.pk % 3 if self.pk else 0]
        if self.status == "yetkazildi" and not self.delivered_at:
            self.delivered_at = timezone.now()
        super().save(*args, **kwargs)

        if not is_new and old_status and old_status != self.status:
            from notifications.services import notify
            notify(
                self.user,
                "Buyurtma holati yangilandi",
                f"Buyurtma #{self.pk}: {self.get_status_display()}",
                link="/my-orders/",
            )

    STATUS_STEPS = ["yangi", "tasdiqlangan", "tayyorlanmoqda", "yetkazilmoqda", "yetkazildi"]

    @property
    def status_step_index(self):
        try:
            return self.STATUS_STEPS.index(self.status)
        except ValueError:
            return -1

    @property
    def can_cancel(self):
        return self.status in ("yangi", "tasdiqlangan")

    @property
    def refund_deadline(self):
        if not self.delivered_at:
            return None
        return self.delivered_at + timezone.timedelta(hours=settings.REFUND_WINDOW_HOURS)

    @property
    def refund_hours_left(self):
        deadline = self.refund_deadline
        if not deadline:
            return 0
        delta = deadline - timezone.now()
        return max(0, int(delta.total_seconds() // 3600))

    @property
    def can_request_refund(self):
        if self.status != "yetkazildi":
            return False
        if hasattr(self, "refund_request"):
            return False
        return self.refund_hours_left > 0


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name="Buyurtma", related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name="Mahsulot", null=True, on_delete=models.SET_NULL)
    product_name = models.CharField("Mahsulot nomi", max_length=150)
    image_url = models.URLField("Rasm manzili", max_length=500, blank=True)
    price = models.DecimalField("Narx", max_digits=12, decimal_places=0)
    quantity = models.PositiveIntegerField("Miqdor", default=1)

    class Meta:
        verbose_name = "Buyurtma mahsuloti"
        verbose_name_plural = "Buyurtma mahsulotlari"

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    @property
    def line_total(self):
        return self.price * self.quantity
