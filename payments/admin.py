from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "provider", "amount", "state", "created_at", "performed_at")
    list_filter = ("provider", "state")
    search_fields = ("order__id", "provider_transaction_id")
    readonly_fields = ("order", "provider", "amount", "provider_transaction_id", "created_at", "performed_at", "cancelled_at")
