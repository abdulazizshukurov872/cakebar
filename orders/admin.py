from django.contrib import admin, messages

from .models import Courier, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "image_url", "price", "quantity", "weight_kg", "inscription")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_amount", "payment_method", "status", "delivery_date", "delivery_slot", "courier", "created_at")
    list_filter = ("status", "payment_method", "delivery_date", "courier")
    list_editable = ("status",)
    search_fields = ("user__username", "user__email", "user__phone")
    inlines = [OrderItemInline]
    readonly_fields = ("created_at", "delivered_at", "total_amount", "delivery_fee")

    def save_model(self, request, obj, form, change):
        # Cancelling must go through Order.cancel() so stock, points and
        # money are returned — a plain status change would skip all that.
        if change and obj.status == "bekor":
            previous = Order.objects.filter(pk=obj.pk).values_list("status", flat=True).first()
            if previous != "bekor":
                obj.status = previous
                super().save_model(request, obj, form, change)
                try:
                    refunded = obj.cancel(reason="do'kon tomonidan bekor qilindi")
                except ValueError as exc:
                    self.message_user(request, f"#{obj.pk}: {exc}", level=messages.ERROR)
                    return
                if refunded:
                    self.message_user(request, f"#{obj.pk}: {refunded:.0f} so'm mijozning walletiga qaytarildi.")
                return
        super().save_model(request, obj, form, change)


@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "user", "is_active")
    list_editable = ("is_active",)
    search_fields = ("name", "phone")
    autocomplete_fields = ("user",)
