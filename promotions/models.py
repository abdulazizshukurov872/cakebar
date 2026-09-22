from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class PromoCode(models.Model):
    code = models.CharField("Kod", max_length=32, unique=True)
    description = models.CharField("Tavsif", max_length=150, blank=True)
    discount_percent = models.PositiveSmallIntegerField("Chegirma (%)", validators=[MinValueValidator(1), MaxValueValidator(100)])
    valid_until = models.DateTimeField("Amal qilish muddati", null=True, blank=True)
    max_uses = models.PositiveIntegerField("Maksimal ishlatilish soni", null=True, blank=True)
    used_count = models.PositiveIntegerField("Ishlatilgan soni", default=0)
    active = models.BooleanField("Faol", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Promo-kod"
        verbose_name_plural = "Promo-kodlar"

    def __str__(self):
        return f"{self.code} (-{self.discount_percent}%)"

    def save(self, *args, **kwargs):
        self.code = self.code.strip().upper()
        super().save(*args, **kwargs)

    def is_valid(self):
        if not self.active:
            return False
        if self.valid_until and timezone.now() > self.valid_until:
            return False
        if self.max_uses is not None and self.used_count >= self.max_uses:
            return False
        return True
