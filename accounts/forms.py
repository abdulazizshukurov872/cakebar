import secrets
import string

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password

from .models import Address, User


def generate_recovery_code():
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(10))


UZ_PASSWORD_ERRORS = {
    "password_too_short": "Parol juda qisqa — kamida 8 belgi bo'lsin.",
    "password_too_common": "Bu parol juda oddiy va keng tarqalgan.",
    "password_entirely_numeric": "Parol faqat raqamlardan iborat bo'lmasin.",
    "password_too_similar": "Parol telefon raqamingizga juda o'xshash.",
}


def check_password_strength(form, field, password, user):
    try:
        validate_password(password, user=user)
    except forms.ValidationError as exc:
        for error in exc.error_list:
            form.add_error(field, UZ_PASSWORD_ERRORS.get(error.code, error.messages[0]))


def create_user(phone, password_hash, referred_by=None, phone_verified=False):
    """Create the account; returns the user with .plain_recovery_code set
    (shown once on the sign-up success page)."""
    recovery_code = generate_recovery_code()
    user = User(
        username=phone, phone=phone,
        password=password_hash,
        recovery_code_hash=make_password(recovery_code),
        referred_by=referred_by,
        phone_verified=phone_verified,
    )
    user.save()
    user.plain_recovery_code = recovery_code
    return user


class SignUpForm(forms.Form):
    phone = forms.CharField(label="Telefon raqam", max_length=32, widget=forms.TextInput(attrs={"placeholder": "+998 90 123 45 67", "autofocus": True}))
    password = forms.CharField(label="Parol", widget=forms.PasswordInput, help_text="Kamida 8 belgi, faqat raqamlardan iborat bo'lmasin.")

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        digits = "".join(ch for ch in phone if ch.isdigit())
        if len(digits) < 9:
            raise forms.ValidationError("Telefon raqamni to'liq kiriting")
        if User.objects.filter(username=phone).exists():
            raise forms.ValidationError("Bu telefon raqam bilan hisob allaqachon mavjud")
        return phone

    def clean(self):
        cleaned = super().clean()
        password, phone = cleaned.get("password"), cleaned.get("phone")
        if password:
            check_password_strength(self, "password", password, User(username=phone or "", phone=phone or ""))
        return cleaned

    def save(self, referred_by=None, phone_verified=False):
        return create_user(
            self.cleaned_data["phone"], make_password(self.cleaned_data["password"]),
            referred_by=referred_by, phone_verified=phone_verified,
        )


class PhoneCodeForm(forms.Form):
    code = forms.CharField(label="SMS kod", max_length=6, min_length=6, widget=forms.TextInput(attrs={"inputmode": "numeric", "autocomplete": "one-time-code", "autofocus": True}))


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
        fields = ("label", "address_line", "latitude", "longitude", "is_default")
        labels = {"label": "Nomi (Uy, Ish...)", "address_line": "To'liq manzil", "is_default": "Asosiy manzil qilish"}
        widgets = {
            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput(),
        }


class PasswordResetForm(forms.Form):
    phone = forms.CharField(label="Telefon raqam", max_length=32)
    recovery_code = forms.CharField(label="Tiklash kodi", max_length=10, widget=forms.TextInput(attrs={"placeholder": "Ro'yxatdan o'tishda berilgan kod"}))
    new_password = forms.CharField(label="Yangi parol", widget=forms.PasswordInput, help_text="Kamida 8 belgi, faqat raqamlardan iborat bo'lmasin.")

    def clean(self):
        cleaned = super().clean()
        phone = cleaned.get("phone", "").strip()
        code = cleaned.get("recovery_code", "").strip().upper()
        if phone and code:
            user = User.objects.filter(username=phone).first()
            if not user or not user.recovery_code_hash or not check_password(code, user.recovery_code_hash):
                raise forms.ValidationError("Telefon raqam yoki tiklash kodi noto'g'ri")
            self.user = user
            new_password = cleaned.get("new_password")
            if new_password:
                check_password_strength(self, "new_password", new_password, user)
        return cleaned

    def save(self):
        self.user.set_password(self.cleaned_data["new_password"])
        self.user.save(update_fields=["password"])
        return self.user
