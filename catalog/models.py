from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField("Nomi", max_length=100)
    parent = models.ForeignKey(
        "self", verbose_name="Ota kategoriya", null=True, blank=True,
        related_name="children", on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField("Nomi", max_length=150)
    description = models.TextField("Tavsif", blank=True)
    composition = models.TextField("Tarkibi", blank=True, help_text="Masalan: un, shakar, tuxum, sariyog', vanil")
    image_url = models.URLField("Rasm manzili (URL)", max_length=500, blank=True)
    category = models.ForeignKey(Category, verbose_name="Kategoriya", related_name="products", on_delete=models.CASCADE)
    price = models.DecimalField("Narx", max_digits=12, decimal_places=0)
    discount_price = models.DecimalField("Chegirma narx", max_digits=12, decimal_places=0, null=True, blank=True)
    in_stock = models.BooleanField("Mavjud", default=True)
    rating = models.DecimalField("Reyting", max_digits=2, decimal_places=1, default=4.5)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def current_price(self):
        return self.discount_price or self.price


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
