import secrets
import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from notifications import eskiz

from . import ratelimit
from .forms import AddressForm, PasswordResetForm, PhoneCodeForm, PhoneLoginForm, ProfileForm, SignUpForm, create_user
from .models import Address, User

SIGNUP_SESSION_KEY = "pending_signup"
SMS_CODE_TTL_SECONDS = 5 * 60
SMS_RESEND_COOLDOWN_SECONDS = 60
SMS_CODE_MAX_ATTEMPTS = 5


class RateLimitedLoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    authentication_form = PhoneLoginForm

    def post(self, request, *args, **kwargs):
        phone = request.POST.get("username", "")
        if ratelimit.is_limited("login", request, phone):
            form = self.get_form()
            form.errors.clear()
            form.add_error(None, ratelimit.limited_message())
            return self.form_invalid(form)
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        if not ratelimit.is_limited("login", self.request, self.request.POST.get("username", "")):
            ratelimit.hit("login", self.request, self.request.POST.get("username", ""))
        return super().form_invalid(form)

    def form_valid(self, form):
        ratelimit.reset("login", self.request, self.request.POST.get("username", ""))
        return super().form_valid(form)


def _sms_verification_enabled():
    return settings.PHONE_VERIFICATION and eskiz.is_configured()


def _send_signup_code(request, pending):
    code = f"{secrets.randbelow(10**6):06d}"
    pending.update({
        "code_hash": make_password(code),
        "expires_at": time.time() + SMS_CODE_TTL_SECONDS,
        "sent_at": time.time(),
        "attempts": 0,
    })
    request.session[SIGNUP_SESSION_KEY] = pending
    return eskiz.send_sms(pending["phone"], f"CakeBar tasdiqlash kodi: {code}. Uni hech kimga bermang.")


def _finish_signup(request, user):
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return render(request, "accounts/signup_success.html", {"recovery_code": user.plain_recovery_code})


def signup(request):
    ref_code = request.GET.get("ref", "").strip().upper()
    referrer = User.objects.filter(referral_code=ref_code).first() if ref_code else None
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if ratelimit.is_limited("signup", request, request.POST.get("phone", "")):
            form.is_valid()
            form.add_error(None, ratelimit.limited_message())
        elif form.is_valid():
            ratelimit.hit("signup", request, form.cleaned_data["phone"])
            if not _sms_verification_enabled():
                return _finish_signup(request, form.save(referred_by=referrer))
            pending = {
                "phone": form.cleaned_data["phone"],
                "password_hash": make_password(form.cleaned_data["password"]),
                "referrer_id": referrer.pk if referrer else None,
            }
            if _send_signup_code(request, pending):
                return redirect("signup_verify")
            form.add_error(None, "SMS yuborib bo'lmadi. Birozdan keyin qayta urinib ko'ring.")
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form, "referrer": referrer})


def signup_verify(request):
    pending = request.session.get(SIGNUP_SESSION_KEY)
    if not pending:
        return redirect("signup")

    form = PhoneCodeForm(request.POST or None)
    if request.method == "POST" and "resend" in request.POST:
        wait = SMS_RESEND_COOLDOWN_SECONDS - (time.time() - pending["sent_at"])
        if wait > 0:
            messages.error(request, f"Yangi kodni {int(wait) + 1} soniyadan keyin so'rashingiz mumkin.")
        elif ratelimit.is_limited("signup", request, pending["phone"]):
            messages.error(request, ratelimit.limited_message())
        else:
            ratelimit.hit("signup", request, pending["phone"])
            _send_signup_code(request, pending)
            messages.success(request, "Yangi kod yuborildi.")
        return redirect("signup_verify")

    if request.method == "POST" and form.is_valid():
        if time.time() > pending["expires_at"] or pending["attempts"] >= SMS_CODE_MAX_ATTEMPTS:
            form.add_error("code", "Kod muddati tugagan yoki urinishlar tugadi — yangi kod so'rang.")
        elif not check_password(form.cleaned_data["code"], pending["code_hash"]):
            pending["attempts"] += 1
            request.session[SIGNUP_SESSION_KEY] = pending
            form.add_error("code", "Kod noto'g'ri.")
        elif User.objects.filter(username=pending["phone"]).exists():
            del request.session[SIGNUP_SESSION_KEY]
            messages.error(request, "Bu telefon raqam bilan hisob allaqachon mavjud.")
            return redirect("login")
        else:
            del request.session[SIGNUP_SESSION_KEY]
            referrer = User.objects.filter(pk=pending["referrer_id"]).first() if pending["referrer_id"] else None
            user = create_user(pending["phone"], pending["password_hash"], referred_by=referrer, phone_verified=True)
            return _finish_signup(request, user)

    return render(request, "accounts/signup_verify.html", {"form": form, "phone": pending["phone"]})


def password_reset(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        phone = request.POST.get("phone", "")
        if ratelimit.is_limited("password_reset", request, phone):
            form.is_valid()
            form.add_error(None, ratelimit.limited_message())
        elif form.is_valid():
            ratelimit.reset("password_reset", request, phone)
            form.save()
            messages.success(request, "Parol muvaffaqiyatli yangilandi. Endi kirishingiz mumkin.")
            return redirect("login")
        else:
            ratelimit.hit("password_reset", request, phone)
    else:
        form = PasswordResetForm()
    return render(request, "accounts/password_reset.html", {"form": form})


@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            new_phone = form.cleaned_data["phone"].strip()
            if new_phone and new_phone != request.user.username and User.objects.filter(username=new_phone).exclude(pk=request.user.pk).exists():
                messages.error(request, "Bu telefon raqam bilan boshqa hisob allaqachon mavjud")
                return render(request, "accounts/profile.html", {"form": form, "addresses": Address.objects.filter(user=request.user), "address_form": AddressForm(), "active": "profile"})
            user = form.save(commit=False)
            if new_phone:
                if new_phone != request.user.username:
                    user.phone_verified = False
                user.username = new_phone
            user.save()
            messages.success(request, "Profil saqlandi")
            return redirect("profile")
    else:
        form = ProfileForm(instance=request.user)
    addresses = Address.objects.filter(user=request.user)
    return render(request, "accounts/profile.html", {"form": form, "addresses": addresses, "address_form": AddressForm(), "active": "profile"})


@login_required
@require_POST
def address_add(request):
    form = AddressForm(request.POST)
    if form.is_valid():
        address = form.save(commit=False)
        address.user = request.user
        address.save()
        messages.success(request, "Manzil qo'shildi")
    else:
        messages.error(request, "Manzilni to'g'ri kiriting")
    return redirect("profile")


@login_required
@require_POST
def address_delete(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    messages.success(request, "Manzil o'chirildi")
    return redirect("profile")
