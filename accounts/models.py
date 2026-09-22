from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField("Telefon", max_length=32, blank=True)
    address = models.CharField("Manzil", max_length=255, blank=True)
    balance = models.DecimalField("Wallet balansi", max_digits=12, decimal_places=0, default=0)

    def __str__(self):
        return self.get_full_name() or self.username
