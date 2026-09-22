from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .models import Category, Favorite, Product


def home(request):
    categories = Category.objects.filter(parent__isnull=True)
    featured = Product.objects.filter(discount_price__isnull=False)[:6]
    if not featured:
        featured = Product.objects.all()[:6]
    favorite_ids = set()
    if request.user.is_authenticated:
        favorite_ids = set(Favorite.objects.filter(user=request.user).values_list("product_id", flat=True))
    return render(request, "catalog/home.html", {"categories": categories, "featured": featured, "favorite_ids": favorite_ids})


def product_list(request):
    products = Product.objects.select_related("category").all()
    category_id = request.GET.get("category")
    q = request.GET.get("q", "").strip()
    if category_id:
        products = products.filter(category_id=category_id)
    if q:
        products = products.filter(name__icontains=q)
    categories = Category.objects.all()
    favorite_ids = set()
    if request.user.is_authenticated:
        favorite_ids = set(Favorite.objects.filter(user=request.user).values_list("product_id", flat=True))
    return render(request, "catalog/product_list.html", {
        "products": products,
        "categories": categories,
        "selected_category": category_id,
        "query": q,
        "favorite_ids": favorite_ids,
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product.objects.select_related("category"), id=product_id)
    favorite_ids = set()
    if request.user.is_authenticated:
        favorite_ids = set(Favorite.objects.filter(user=request.user).values_list("product_id", flat=True))
    related = Product.objects.filter(category=product.category).exclude(id=product.id)[:3]
    return render(request, "catalog/product_detail.html", {
        "p": product, "is_favorite": product.id in favorite_ids, "related": related, "favorite_ids": favorite_ids,
    })


@require_POST
def favorite_toggle(request, product_id):
    if not request.user.is_authenticated:
        messages.info(request, "Sevimlilarga qo'shish uchun avval tizimga kiring.")
        next_url = request.POST.get("next", "")
        login_url = f"{reverse('login')}?next={next_url}" if next_url else reverse("login")
        return redirect(login_url)

    product = get_object_or_404(Product, id=product_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if not created:
        fav.delete()
        messages.success(request, "Sevimlilardan olib tashlandi")
    else:
        messages.success(request, "Sevimlilarga qo'shildi")
    next_url = request.POST.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect("product_list")


@login_required
def favorite_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related("product", "product__category")
    products = [f.product for f in favorites]
    favorite_ids = {p.id for p in products}
    return render(request, "catalog/favorite_list.html", {"products": products, "favorite_ids": favorite_ids, "active": "favorites"})
