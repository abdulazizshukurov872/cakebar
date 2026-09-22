from django.contrib import admin

from .models import Category, Favorite, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "discount_price", "stock_quantity", "in_stock", "rating")
    list_filter = ("category", "in_stock")
    list_editable = ("discount_price", "stock_quantity")
    readonly_fields = ("in_stock",)
    search_fields = ("name", "composition")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    search_fields = ("user__username", "product__name")
