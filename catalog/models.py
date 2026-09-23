from decimal import Decimal

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
    quantity = models.CharField("Miqdori/og'irligi (uz)", max_length=50, blank=True, help_text="Masalan: 1.5 kg, 6 dona, 500 ml")
    quantity_ru = models.CharField("Miqdori/og'irligi (ru)", max_length=50, blank=True)
    quantity_en = models.CharField("Miqdori/og'irligi (en)", max_length=50, blank=True)
    image_url = models.URLField("Rasm manzili (URL)", max_length=500, blank=True)
    image = models.ImageField("Rasm (yuklash)", upload_to="products/", blank=True, null=True,
                               help_text="Kompyuterdan rasm yuklang. Bo'sh qoldirilsa, yuqoridagi URL ishlatiladi.")
    category = models.ForeignKey(Category, verbose_name="Kategoriya", related_name="products", on_delete=models.CASCADE)
    price = models.DecimalField("Narx", max_digits=12, decimal_places=0)
    discount_price = models.DecimalField("Chegirma narx", max_digits=12, decimal_places=0, null=True, blank=True)
    sold_by_weight = models.BooleanField(
        "Og'irlik bo'yicha sotiladi", default=False,
        help_text="Belgilansa, narx 1 kg uchun hisoblanadi va mijoz og'irlikni (1–3 kg) o'zi tanlaydi.",
    )
    allows_inscription = models.BooleanField(
        "Yozuv yozish mumkin", default=False,
        help_text="Mijoz tort ustiga yoziladigan matnni kiritishi mumkin.",
    )
    in_stock = models.BooleanField("Mavjud", default=True)
    stock_quantity = models.PositiveIntegerField("Zaxira miqdori", default=20)
    rating = models.DecimalField("Reyting", max_digits=2, decimal_places=1, default=4.5)
    calories = models.PositiveIntegerField("Kaloriya (kkal, 100gr)", null=True, blank=True)
    protein_g = models.DecimalField("Oqsil (gr, 100gr)", max_digits=5, decimal_places=1, null=True, blank=True)
    fat_g = models.DecimalField("Yog' (gr, 100gr)", max_digits=5, decimal_places=1, null=True, blank=True)
    carbs_g = models.DecimalField("Uglevod (gr, 100gr)", max_digits=5, decimal_places=1, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.in_stock = self.stock_quantity > 0
        super().save(*args, **kwargs)

    def reduce_stock(self, quantity):
        self.stock_quantity = max(0, self.stock_quantity - quantity)
        self.in_stock = self.stock_quantity > 0
        self.save(update_fields=["stock_quantity", "in_stock"])

    WEIGHT_OPTIONS = ["1", "1.5", "2", "2.5", "3"]

    @property
    def current_price(self):
        return self.discount_price or self.price

    def unit_price(self, weight_kg=None):
        """Price of one cart unit: per-kg products are multiplied by the chosen weight."""
        if self.sold_by_weight and weight_kg:
            return (self.current_price * Decimal(str(weight_kg))).quantize(Decimal("1"))
        return self.current_price

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        return self.image_url

    @property
    def calorie_level(self):
        """Rough guide: under 150 kcal/100g = light, 150-300 = medium, 300+ = high."""
        if self.calories is None:
            return None
        if self.calories < 150:
            return "past"
        if self.calories < 300:
            return "orta"
        return "yuqori"

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
