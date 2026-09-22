from django.contrib import admin

from .models import RefundRequest


@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "user", "reason", "status", "refund_amount", "requested_at")
    list_filter = ("status", "reason")
    search_fields = ("order__id", "user__username", "user__phone", "comment")
    readonly_fields = ("order", "user", "reason", "comment", "image", "requested_at", "resolved_at")
    fields = (
        "order", "user", "reason", "comment", "image",
        "status", "refund_amount", "admin_comment",
        "requested_at", "resolved_at",
    )

    actions = ["approve_selected", "reject_selected"]

    def save_model(self, request, obj, form, change):
        previous_status = None
        if change:
            previous_status = RefundRequest.objects.get(pk=obj.pk).status

        if previous_status != "tasdiqlandi" and obj.status == "tasdiqlandi":
            amount = obj.refund_amount or obj.order.total_amount
            obj.approve(amount, obj.admin_comment)
            return
        if previous_status != "rad_etildi" and obj.status == "rad_etildi":
            obj.reject(obj.admin_comment)
            return
        super().save_model(request, obj, form, change)

    @admin.action(description="Tanlanganlarni tasdiqlash (to'liq summa)")
    def approve_selected(self, request, queryset):
        count = 0
        for refund in queryset.filter(status="kutilmoqda"):
            refund.approve(refund.order.total_amount, "Ommaviy tasdiqlandi")
            count += 1
        self.message_user(request, f"{count} ta so'rov tasdiqlandi.")

    @admin.action(description="Tanlanganlarni rad etish")
    def reject_selected(self, request, queryset):
        count = 0
        for refund in queryset.filter(status="kutilmoqda"):
            refund.reject("Ommaviy rad etildi")
            count += 1
        self.message_user(request, f"{count} ta so'rov rad etildi.")
