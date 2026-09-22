from django.contrib import admin

from .models import JobOpening, Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "phone", "working_hours", "order")
    list_editable = ("order",)


@admin.register(JobOpening)
class JobOpeningAdmin(admin.ModelAdmin):
    list_display = ("title", "department", "location", "is_active")
    list_editable = ("is_active",)
