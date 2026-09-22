from django import forms

from .models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("address", "payment_method")
        labels = {
            "address": "Yetkazib berish manzili",
            "payment_method": "To'lov usuli",
        }
