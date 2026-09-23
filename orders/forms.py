import datetime

from django import forms
from django.conf import settings
from django.utils import timezone

from .models import Order

UZ_WEEKDAYS = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]


def delivery_date_choices(now=None):
    today = timezone.localdate(now)
    choices = []
    for offset in range(settings.DELIVERY_DAYS_AHEAD):
        day = today + datetime.timedelta(days=offset)
        prefix = {0: "Bugun", 1: "Ertaga"}.get(offset, UZ_WEEKDAYS[day.weekday()])
        choices.append((day.isoformat(), f"{prefix}, {day:%d.%m}"))
    return choices


def slot_is_available(day, slot, now=None):
    """A slot can still be booked if it starts at least DELIVERY_LEAD_HOURS from now."""
    now = timezone.localtime(now or timezone.now())
    start_hour = int(slot.split("-")[0])
    start = timezone.make_aware(datetime.datetime.combine(day, datetime.time(hour=start_hour)))
    return start >= now + datetime.timedelta(hours=settings.DELIVERY_LEAD_HOURS)


class CheckoutForm(forms.ModelForm):
    delivery_date = forms.ChoiceField(label="Yetkazish kuni")
    delivery_slot = forms.ChoiceField(label="Yetkazish vaqti", choices=Order.DELIVERY_SLOTS)
    promo_code = forms.CharField(label="Promo-kod", max_length=32, required=False, widget=forms.TextInput(attrs={"placeholder": "Bo'lsa, kiriting"}))
    use_points = forms.BooleanField(label="Ball(lar)imni chegirma sifatida ishlataman", required=False)

    class Meta:
        model = Order
        fields = ("address", "latitude", "longitude", "payment_method")
        labels = {
            "address": "Yetkazib berish manzili",
            "payment_method": "To'lov usuli",
        }
        widgets = {
            "address": forms.TextInput(attrs={"list": "saved-addresses"}),
            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["delivery_date"].choices = delivery_date_choices()
        if not self.is_bound:
            self.initial.setdefault("delivery_date", self.first_available()[0])
            self.initial.setdefault("delivery_slot", self.first_available()[1])

    @staticmethod
    def first_available():
        for value, _ in delivery_date_choices():
            day = datetime.date.fromisoformat(value)
            for slot, _ in Order.DELIVERY_SLOTS:
                if slot_is_available(day, slot):
                    return value, slot
        return None, None

    def clean_delivery_date(self):
        return datetime.date.fromisoformat(self.cleaned_data["delivery_date"])

    def clean(self):
        cleaned = super().clean()
        day, slot = cleaned.get("delivery_date"), cleaned.get("delivery_slot")
        if day and slot and not slot_is_available(day, slot):
            self.add_error(
                "delivery_slot",
                f"Bu vaqt oralig'i uchun kech — kamida {settings.DELIVERY_LEAD_HOURS} soat oldin buyurtma bering.",
            )
        return cleaned
