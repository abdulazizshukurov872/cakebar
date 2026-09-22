from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import AddressForm, PasswordResetForm, ProfileForm, SignUpForm
from .models import Address, User


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return render(request, "accounts/signup_success.html", {"recovery_code": user.plain_recovery_code})
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})


def password_reset(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Parol muvaffaqiyatli yangilandi. Endi kirishingiz mumkin.")
            return redirect("login")
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
