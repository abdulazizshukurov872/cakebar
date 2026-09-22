from django.contrib import admin

from .models import PromoCode


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_percent", "used_count", "max_uses", "valid_until", "active")
    list_editable = ("active",)
    search_fields = ("code",)
