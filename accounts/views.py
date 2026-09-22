from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import AddressForm, ProfileForm, SignUpForm
from .models import Address


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Xush kelibsiz, {user.username}!")
            return redirect("dashboard")
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})


@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
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
