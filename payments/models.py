from django.db import models

from orders.models import Order


class Payment(models.Model):
    PROVIDER_CHOICES = [
        ("payme", "Payme"),
        ("click", "Click"),
    ]
    STATE_CHOICES = [
        ("created", "Yaratildi (kutilmoqda)"),
        ("performed", "To'landi"),
        ("cancelled", "Bekor qilindi"),
    ]

    order = models.OneToOneField(Order, verbose_name="Buyurtma", related_name="payment", on_delete=models.CASCADE)
    provider = models.CharField("Provayder", max_length=10, choices=PROVIDER_CHOICES)
    amount = models.DecimalField("Summa (so'm)", max_digits=12, decimal_places=0)
    state = models.CharField("Holati", max_length=12, choices=STATE_CHOICES, default="created")
    provider_transaction_id = models.CharField("Provayder tranzaksiya ID", max_length=64, blank=True)
    error_reason = models.CharField("Xato sababi", max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    performed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "To'lov"
        verbose_name_plural = "To'lovlar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_provider_display()} — buyurtma #{self.order_id} ({self.get_state_display()})"
