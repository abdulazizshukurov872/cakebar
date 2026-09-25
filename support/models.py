from django.conf import settings
from django.db import models


class ChatMessage(models.Model):
    """One customer <-> staff support thread per customer. `customer` is
    always the thread owner; `sender` is whoever actually wrote this
    message (the customer themself, or a staff member replying)."""

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="Mijoz",
        related_name="support_thread", on_delete=models.CASCADE,
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="Yuboruvchi",
        related_name="sent_chat_messages", on_delete=models.CASCADE,
    )
    is_from_admin = models.BooleanField("Admindan", default=False)
    text = models.TextField("Xabar matni", max_length=2000)
    read_by_customer = models.BooleanField(default=False)
    read_by_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Chat xabari"
        verbose_name_plural = "Chat xabarlari"
        ordering = ["created_at"]

    def __str__(self):
        who = "admin" if self.is_from_admin else "mijoz"
        return f"{self.customer} ({who}): {self.text[:40]}"
