from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField("Telefon", max_length=32, blank=True)
    address = models.CharField("Manzil", max_length=255, blank=True)
    balance = models.DecimalField("Wallet balansi", max_digits=12, decimal_places=0, default=0)
    loyalty_points = models.PositiveIntegerField("Loyallik ballari", default=0)
    recovery_code_hash = models.CharField("Tiklash kodi (hash)", max_length=128, blank=True)

    def __str__(self):
        return self.get_full_name() or self.username


class Address(models.Model):
    user = models.ForeignKey(User, verbose_name="Foydalanuvchi", related_name="addresses", on_delete=models.CASCADE)
    label = models.CharField("Nomi", max_length=50, help_text="Masalan: Uy, Ish")
    address_line = models.CharField("Manzil", max_length=255)
    is_default = models.BooleanField("Asosiy", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Manzil"
        verbose_name_plural = "Manzillar"
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.label}: {self.address_line}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_default:
            Address.objects.filter(user=self.user).exclude(pk=self.pk).update(is_default=False)
