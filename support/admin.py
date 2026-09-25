from django.contrib import admin

from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("customer", "sender", "is_from_admin", "text", "created_at")
    list_filter = ("is_from_admin",)
    search_fields = ("customer__username", "customer__phone", "text")
