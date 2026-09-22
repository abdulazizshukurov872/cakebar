from django.db import models


class Location(models.Model):
    name = models.CharField("Nomi", max_length=150)
    address = models.CharField("Manzil", max_length=255)
    phone = models.CharField("Telefon", max_length=32)
    working_hours = models.CharField("Ish vaqti", max_length=100, default="09:00 – 22:00")
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        verbose_name = "Filial"
        verbose_name_plural = "Filiallar"
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class JobOpening(models.Model):
    title = models.CharField("Lavozim", max_length=150)
    department = models.CharField("Bo'lim", max_length=100, blank=True)
    location = models.CharField("Joylashuv", max_length=150, default="Toshkent")
    description = models.TextField("Tavsif", blank=True)
    is_active = models.BooleanField("Faol", default=True)

    class Meta:
        verbose_name = "Bo'sh ish o'rni"
        verbose_name_plural = "Bo'sh ish o'rinlari"

    def __str__(self):
        return self.title
