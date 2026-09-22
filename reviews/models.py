from django.conf import settings
from django.db import models

from catalog.models import Product


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    product = models.ForeignKey(Product, verbose_name="Mahsulot", related_name="reviews", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Foydalanuvchi", related_name="reviews", on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField("Baho", choices=RATING_CHOICES)
    comment = models.TextField("Izoh", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sharh"
        verbose_name_plural = "Sharhlar"
        ordering = ["-created_at"]
        unique_together = ("product", "user")

    def __str__(self):
        return f"{self.product} — {self.rating}★ ({self.user})"
