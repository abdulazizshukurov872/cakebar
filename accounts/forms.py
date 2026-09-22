from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import User


class SignUpForm(forms.Form):
    phone = forms.CharField(label="Telefon raqam", max_length=32, widget=forms.TextInput(attrs={"placeholder": "+998 90 123 45 67", "autofocus": True}))
    password = forms.CharField(label="Parol", widget=forms.PasswordInput, min_length=4)

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if User.objects.filter(username=phone).exists():
            raise forms.ValidationError("Bu telefon raqam bilan hisob allaqachon mavjud")
        return phone

    def save(self):
        user = User(username=self.cleaned_data["phone"], phone=self.cleaned_data["phone"])
        user.set_password(self.cleaned_data["password"])
        user.save()
        return user


class PhoneLoginForm(AuthenticationForm):
    username = forms.CharField(label="Telefon raqam")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone", "address")
        labels = {
            "first_name": "Ism",
            "last_name": "Familiya",
            "phone": "Telefon",
            "address": "Manzil",
        }
