from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "image_url", "price", "quantity")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_amount", "payment_method", "status", "created_at")
    list_filter = ("status", "payment_method")
    list_editable = ("status",)
    search_fields = ("user__username", "user__email")
    inlines = [OrderItemInline]
    readonly_fields = ("created_at", "delivered_at", "total_amount")
