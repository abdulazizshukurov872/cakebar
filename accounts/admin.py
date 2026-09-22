from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CakeBarUserAdmin(UserAdmin):
    list_display = ("username", "email", "phone", "balance", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        ("CakeBar ma'lumotlari", {"fields": ("phone", "address", "balance")}),
    )
