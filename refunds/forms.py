from django import forms

from .models import RefundRequest


class RefundRequestForm(forms.ModelForm):
    class Meta:
        model = RefundRequest
        fields = ("reason", "comment", "image")
        labels = {
            "reason": "Sabab",
            "comment": "Izoh",
            "image": "Rasm biriktirish (ixtiyoriy)",
        }
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 3, "placeholder": "Qo'shimcha izoh (ixtiyoriy)"}),
        }
