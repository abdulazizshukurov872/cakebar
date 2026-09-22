import secrets
import string

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import check_password, make_password

from .models import Address, User


def generate_recovery_code():
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(10))


class SignUpForm(forms.Form):
    phone = forms.CharField(label="Telefon raqam", max_length=32, widget=forms.TextInput(attrs={"placeholder": "+998 90 123 45 67", "autofocus": True}))
    password = forms.CharField(label="Parol", widget=forms.PasswordInput, min_length=4)

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if User.objects.filter(username=phone).exists():
            raise forms.ValidationError("Bu telefon raqam bilan hisob allaqachon mavjud")
        return phone

    def save(self):
        recovery_code = generate_recovery_code()
        user = User(
            username=self.cleaned_data["phone"], phone=self.cleaned_data["phone"],
            recovery_code_hash=make_password(recovery_code),
        )
        user.set_password(self.cleaned_data["password"])
        user.save()
        user.plain_recovery_code = recovery_code
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


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ("label", "address_line", "is_default")
        labels = {"label": "Nomi (Uy, Ish...)", "address_line": "To'liq manzil", "is_default": "Asosiy manzil qilish"}


class PasswordResetForm(forms.Form):
    phone = forms.CharField(label="Telefon raqam", max_length=32)
    recovery_code = forms.CharField(label="Tiklash kodi", max_length=10, widget=forms.TextInput(attrs={"placeholder": "Ro'yxatdan o'tishda berilgan kod"}))
    new_password = forms.CharField(label="Yangi parol", widget=forms.PasswordInput, min_length=4)

    def clean(self):
        cleaned = super().clean()
        phone = cleaned.get("phone", "").strip()
        code = cleaned.get("recovery_code", "").strip().upper()
        if phone and code:
            user = User.objects.filter(username=phone).first()
            if not user or not user.recovery_code_hash or not check_password(code, user.recovery_code_hash):
                raise forms.ValidationError("Telefon raqam yoki tiklash kodi noto'g'ri")
            self.user = user
        return cleaned

    def save(self):
        self.user.set_password(self.cleaned_data["new_password"])
        self.user.save(update_fields=["password"])
        return self.user
