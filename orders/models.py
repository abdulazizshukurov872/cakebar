import datetime
from decimal import Decimal

from django.conf import settings
from django.db import models, transaction
from django.db.models import Count, F, Q
from django.utils import timezone

from catalog.models import Product


class Courier(models.Model):
    """A delivery person. Linking a site account lets them use the courier
    panel (/courier/) to see their orders and mark them as delivered."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, verbose_name="Hisob", null=True, blank=True,
        related_name="courier_profile", on_delete=models.SET_NULL,
        help_text="Kuryer panelga kirishi uchun uning saytdagi hisobini tanlang.",
    )
    name = models.CharField("Ismi", max_length=100)
    phone = models.CharField("Telefon", max_length=32)
    is_active = models.BooleanField("Faol", default=True)

    class Meta:
        verbose_name = "Kuryer"
        verbose_name_plural = "Kuryerlar"

    def __str__(self):
        return f"{self.name} ({self.phone})"

    @classmethod
    def least_busy(cls):
        return (
            cls.objects.filter(is_active=True)
            .annotate(active_orders=Count(
                "orders", filter=Q(orders__status__in=Order.ACTIVE_STATUSES),
            ))
            .order_by("active_orders", "id")
            .first()
        )


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
    DELIVERY_SLOTS = [
        ("10-12", "10:00 – 12:00"),
        ("12-14", "12:00 – 14:00"),
        ("14-16", "14:00 – 16:00"),
        ("16-18", "16:00 – 18:00"),
        ("18-20", "18:00 – 20:00"),
        ("20-22", "20:00 – 22:00"),
    ]
    ACTIVE_STATUSES = ("tasdiqlangan", "tayyorlanmoqda", "yetkazilmoqda")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Foydalanuvchi", related_name="orders", on_delete=models.CASCADE)
    address = models.CharField("Yetkazib berish manzili", max_length=255)
    latitude = models.DecimalField("Kenglik", max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField("Uzunlik", max_digits=9, decimal_places=6, null=True, blank=True)
    payment_method = models.CharField("To'lov usuli", max_length=10, choices=PAYMENT_CHOICES, default="naqd")
    status = models.CharField("Status", max_length=20, choices=STATUS_CHOICES, default="yangi")
    total_amount = models.DecimalField("Umumiy summa", max_digits=12, decimal_places=0, default=0)
    delivery_fee = models.DecimalField("Yetkazish narxi", max_digits=12, decimal_places=0, default=0)
    promo_code = models.CharField("Promo-kod", max_length=32, blank=True)
    discount_amount = models.DecimalField("Chegirma summasi", max_digits=12, decimal_places=0, default=0)
    points_used = models.PositiveIntegerField("Ishlatilgan ballar", default=0)
    points_earned = models.PositiveIntegerField("Berilgan ballar", default=0)
    delivery_date = models.DateField("Yetkazish sanasi", null=True, blank=True)
    delivery_slot = models.CharField("Yetkazish vaqti", max_length=5, choices=DELIVERY_SLOTS, blank=True)
    created_at = models.DateTimeField("Yaratilgan sana", auto_now_add=True)
    delivered_at = models.DateTimeField("Yetkazilgan sana", null=True, blank=True)
    estimated_delivery_at = models.DateTimeField("Taxminiy yetkazish vaqti", null=True, blank=True)
    courier = models.ForeignKey(Courier, verbose_name="Kuryer", null=True, blank=True, related_name="orders", on_delete=models.SET_NULL)
    courier_name = models.CharField("Kuryer ismi", max_length=100, blank=True)
    courier_phone = models.CharField("Kuryer telefoni", max_length=32, blank=True)

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Buyurtma #{self.pk} — {self.user}"

    POINTS_PER_SOM = 1000   # 1 ball har 1000 so'mga
    POINT_VALUE = 100       # 1 ball = 100 so'm chegirma
    REFERRAL_BONUS_POINTS = 50
    STATUS_STEPS = ["yangi", "tasdiqlangan", "tayyorlanmoqda", "yetkazilmoqda", "yetkazildi"]

    @property
    def slot_end(self):
        if not (self.delivery_date and self.delivery_slot):
            return None
        end_hour = int(self.delivery_slot.split("-")[1])
        naive = datetime.datetime.combine(self.delivery_date, datetime.time(hour=end_hour % 24))
        return timezone.make_aware(naive)

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        old_status = None
        if not is_new:
            old_status = Order.objects.filter(pk=self.pk).values_list("status", flat=True).first()

        if not self.estimated_delivery_at and self.status != "bekor":
            self.estimated_delivery_at = self.slot_end or (self.created_at or timezone.now()) + timezone.timedelta(hours=2)
        if self.status in self.ACTIVE_STATUSES + ("yetkazildi",) and not self.courier_id:
            courier = Courier.least_busy()
            if courier:
                self.courier = courier
        if self.courier_id and not self.courier_name:
            self.courier_name, self.courier_phone = self.courier.name, self.courier.phone
        if self.status == "yetkazildi" and not self.delivered_at:
            self.delivered_at = timezone.now()
        super().save(*args, **kwargs)

        if not is_new and old_status and old_status != self.status:
            self._on_status_changed()

    def _on_status_changed(self):
        from accounts.models import User
        from notifications.services import notify

        notify(
            self.user,
            "Buyurtma holati yangilandi",
            f"Buyurtma #{self.pk}: {self.get_status_display()}",
            link="/my-orders/",
        )
        if self.status != "yetkazildi":
            return

        if not self.points_earned:
            earned = int(self.total_amount // self.POINTS_PER_SOM)
            # The filter makes this a no-op if a concurrent save already awarded them.
            if earned > 0 and Order.objects.filter(pk=self.pk, points_earned=0).update(points_earned=earned):
                self.points_earned = earned
                User.objects.filter(pk=self.user_id).update(loyalty_points=F("loyalty_points") + earned)
                notify(
                    self.user, "Ball qo'shildi",
                    f"Buyurtma #{self.pk} uchun {earned} ball hisobingizga qo'shildi.",
                    link="/my-orders/",
                )

        if self.user.referred_by_id and not self.user.referral_bonus_awarded:
            is_first_delivered = not Order.objects.filter(
                user=self.user, status="yetkazildi",
            ).exclude(pk=self.pk).exists()
            awarded = is_first_delivered and User.objects.filter(
                pk=self.user_id, referral_bonus_awarded=False,
            ).update(referral_bonus_awarded=True, loyalty_points=F("loyalty_points") + self.REFERRAL_BONUS_POINTS)
            if awarded:
                User.objects.filter(pk=self.user.referred_by_id).update(
                    loyalty_points=F("loyalty_points") + self.REFERRAL_BONUS_POINTS,
                )
                notify(
                    self.user.referred_by, "Referral bonusi",
                    f"Taklif qilgan do'stingiz birinchi buyurtmasini oldi — {self.REFERRAL_BONUS_POINTS} ball qo'shildi!",
                    link="/my-orders/",
                )
                notify(
                    self.user, "Referral bonusi",
                    f"Referral orqali ro'yxatdan o'tganingiz uchun {self.REFERRAL_BONUS_POINTS} ball qo'shildi!",
                    link="/my-orders/",
                )

    @property
    def is_paid_online(self):
        from payments.models import Payment

        return Payment.objects.filter(order_id=self.pk, state="performed").exists()

    def cancel(self, refund_money=True, reason=""):
        """Cancel the order and undo everything checkout did: return stock,
        loyalty points and the promo-code use, and give the money back to the
        wallet if it was already paid (by wallet or online card payment).

        Pass refund_money=False when the payment provider itself has already
        returned the money to the card (e.g. Payme CancelTransaction).

        Safe to call twice or concurrently — only the first call does anything.
        Returns the amount credited to the wallet, or None if the order was
        already cancelled.
        """
        from accounts.models import User
        from notifications.services import notify
        from promotions.models import PromoCode

        with transaction.atomic():
            locked = Order.objects.select_for_update().get(pk=self.pk)
            if locked.status == "bekor":
                return None
            if locked.status in ("yetkazildi", "qaytarildi"):
                raise ValueError("Yetkazilgan buyurtmani bekor qilib bo'lmaydi — qaytarish so'rovidan foydalaning.")

            refunded = Decimal("0")
            if refund_money and (locked.payment_method == "wallet" or locked.is_paid_online):
                refunded = locked.total_amount

            Order.objects.filter(pk=self.pk).update(status="bekor")
            for item in locked.items.all():
                if item.product_id:
                    Product.objects.filter(pk=item.product_id).update(
                        stock_quantity=F("stock_quantity") + item.quantity, in_stock=True,
                    )
            user_updates = {}
            if locked.points_used:
                user_updates["loyalty_points"] = F("loyalty_points") + locked.points_used
            if refunded:
                user_updates["balance"] = F("balance") + refunded
            if user_updates:
                User.objects.filter(pk=locked.user_id).update(**user_updates)
            if locked.promo_code:
                PromoCode.objects.filter(code=locked.promo_code, used_count__gt=0).update(used_count=F("used_count") - 1)

        self.status = "bekor"
        text = f"Buyurtma #{self.pk} bekor qilindi."
        if reason:
            text += f" Sabab: {reason}."
        if refunded:
            text += f" {refunded:.0f} so'm wallet balansingizga qaytarildi."
        notify(self.user, "Buyurtma bekor qilindi", text, link="/my-orders/")
        return refunded

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
    weight_kg = models.DecimalField("Og'irligi (kg)", max_digits=4, decimal_places=1, null=True, blank=True)
    inscription = models.CharField("Tortdagi yozuv", max_length=60, blank=True)

    class Meta:
        verbose_name = "Buyurtma mahsuloti"
        verbose_name_plural = "Buyurtma mahsulotlari"

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    @property
    def line_total(self):
        return self.price * self.quantity
