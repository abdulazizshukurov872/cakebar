from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField("Nomi (uz)", max_length=100)
    name_ru = models.CharField("Nomi (ru)", max_length=100, blank=True)
    name_en = models.CharField("Nomi (en)", max_length=100, blank=True)
    parent = models.ForeignKey(
        "self", verbose_name="Ota kategoriya", null=True, blank=True,
        related_name="children", on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"

    def __str__(self):
        return self.name

    def localized(self, field, lang):
        if lang == "uz":
            return getattr(self, field, "")
        return getattr(self, f"{field}_{lang}", "") or getattr(self, field, "")


class Product(models.Model):
    name = models.CharField("Nomi (uz)", max_length=150)
    name_ru = models.CharField("Nomi (ru)", max_length=150, blank=True)
    name_en = models.CharField("Nomi (en)", max_length=150, blank=True)
    description = models.TextField("Tavsif (uz)", blank=True)
    description_ru = models.TextField("Tavsif (ru)", blank=True)
    description_en = models.TextField("Tavsif (en)", blank=True)
    composition = models.TextField("Tarkibi (uz)", blank=True, help_text="Masalan: un, shakar, tuxum, sariyog', vanil")
    composition_ru = models.TextField("Tarkibi (ru)", blank=True)
    composition_en = models.TextField("Tarkibi (en)", blank=True)
    image_url = models.URLField("Rasm manzili (URL)", max_length=500, blank=True)
    category = models.ForeignKey(Category, verbose_name="Kategoriya", related_name="products", on_delete=models.CASCADE)
    price = models.DecimalField("Narx", max_digits=12, decimal_places=0)
    discount_price = models.DecimalField("Chegirma narx", max_digits=12, decimal_places=0, null=True, blank=True)
    in_stock = models.BooleanField("Mavjud", default=True)
    stock_quantity = models.PositiveIntegerField("Zaxira miqdori", default=20)
    rating = models.DecimalField("Reyting", max_digits=2, decimal_places=1, default=4.5)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.stock_quantity == 0:
            self.in_stock = False
        super().save(*args, **kwargs)

    def reduce_stock(self, quantity):
        self.stock_quantity = max(0, self.stock_quantity - quantity)
        if self.stock_quantity == 0:
            self.in_stock = False
        self.save(update_fields=["stock_quantity", "in_stock"])

    @property
    def current_price(self):
        return self.discount_price or self.price

    def localized(self, field, lang):
        if lang == "uz":
            return getattr(self, field, "")
        return getattr(self, f"{field}_{lang}", "") or getattr(self, field, "")


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Foydalanuvchi", related_name="favorites", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name="Mahsulot", related_name="favorited_by", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sevimli mahsulot"
        verbose_name_plural = "Sevimli mahsulotlar"
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user} ♥ {self.product}"
