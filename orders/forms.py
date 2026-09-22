from django import forms

from .models import Order


class CheckoutForm(forms.ModelForm):
    promo_code = forms.CharField(label="Promo-kod", max_length=32, required=False, widget=forms.TextInput(attrs={"placeholder": "Bo'lsa, kiriting"}))
    use_points = forms.BooleanField(label="Ball(lar)imni chegirma sifatida ishlataman", required=False)

    class Meta:
        model = Order
        fields = ("address", "payment_method")
        labels = {
            "address": "Yetkazib berish manzili",
            "payment_method": "To'lov usuli",
        }
        widgets = {
            "address": forms.TextInput(attrs={"list": "saved-addresses"}),
        }
