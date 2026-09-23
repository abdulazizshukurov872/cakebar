from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Favorite, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "name", "category", "price", "discount_price", "stock_quantity", "in_stock", "rating")
    list_filter = ("category", "in_stock", "sold_by_weight", "allows_inscription")
    list_editable = ("discount_price", "stock_quantity")
    readonly_fields = ("in_stock", "thumbnail")
    search_fields = ("name", "composition")

    def thumbnail(self, obj):
        if obj.display_image:
            return format_html('<img src="{}" style="height:40px;width:40px;object-fit:cover;border-radius:6px;">', obj.display_image)
        return "—"
    thumbnail.short_description = "Rasm"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    search_fields = ("user__username", "product__name")
