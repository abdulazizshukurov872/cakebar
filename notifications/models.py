from django.conf import settings
from django.db import models


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Foydalanuvchi", related_name="notifications", on_delete=models.CASCADE)
    title = models.CharField("Sarlavha", max_length=150)
    message = models.CharField("Xabar", max_length=255)
    link = models.CharField("Havola", max_length=255, blank=True)
    is_read = models.BooleanField("O'qilgan", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Bildirishnoma"
        verbose_name_plural = "Bildirishnomalar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} — {self.title}"
