from django.contrib import admin

from .models import Category, Favorite, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "discount_price", "in_stock", "rating")
    list_filter = ("category", "in_stock")
    list_editable = ("in_stock", "discount_price")
    search_fields = ("name", "composition")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    search_fields = ("user__username", "product__name")
