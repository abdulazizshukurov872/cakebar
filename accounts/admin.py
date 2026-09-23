from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Address, User


@admin.register(User)
class CakeBarUserAdmin(UserAdmin):
    list_display = ("username", "email", "phone", "phone_verified", "balance", "loyalty_points", "is_superuser")
    fieldsets = UserAdmin.fieldsets + (
        ("CakeBar ma'lumotlari", {"fields": ("phone", "phone_verified", "address", "balance", "loyalty_points")}),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "label", "address_line", "is_default")
    search_fields = ("user__username", "address_line")
