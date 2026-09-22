from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "comment")
        labels = {"rating": "Baho", "comment": "Izoh"}
        widgets = {
            "rating": forms.Select(choices=Review.RATING_CHOICES),
            "comment": forms.Textarea(attrs={"rows": 3, "placeholder": "Mahsulot haqida fikringiz (ixtiyoriy)"}),
        }
