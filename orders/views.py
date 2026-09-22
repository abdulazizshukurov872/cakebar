from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from catalog.models import Product

from .cart import Cart
from .forms import CheckoutForm
from .models import Order, OrderItem


def cart_detail(request):
    return render(request, "orders/cart.html", {"cart": Cart(request)})


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, in_stock=True)
    Cart(request).add(product.id, 1)
    messages.success(request, "Savatga qo'shildi")
    next_url = request.POST.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect("product_list")


@require_POST
def cart_update(request, product_id):
    qty = int(request.POST.get("qty", 1))
    Cart(request).update(product_id, qty)
    return redirect("cart_detail")


@require_POST
def cart_remove(request, product_id):
    Cart(request).remove(product_id)
    return redirect("cart_detail")


def checkout(request):
    if not request.user.is_authenticated:
        messages.info(request, "Buyurtma berish uchun avval tizimga kiring yoki ro'yxatdan o'ting.")
        return redirect(f"{reverse('login')}?next={reverse('checkout')}")

    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, "Savat bo'sh — avval mahsulot tanlang")
        return redirect("product_list")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            total = cart.get_total_price()
            payment_method = form.cleaned_data["payment_method"]
            if payment_method == "wallet" and request.user.balance < total:
                messages.error(request, f"Wallet balansingizda yetarli mablag' yo'q ({request.user.balance:.0f} so'm). Boshqa to'lov usulini tanlang.")
                return render(request, "orders/checkout.html", {"form": form, "cart": cart})

            order = form.save(commit=False)
            order.user = request.user
            order.total_amount = total
            order.save()
            for line in cart:
                OrderItem.objects.create(
                    order=order,
                    product=line["product"],
                    product_name=line["product"].name,
                    image_url=line["product"].image_url,
                    price=line["price"],
                    quantity=line["qty"],
                )
            if payment_method == "wallet":
                request.user.balance = request.user.balance - total
                request.user.save(update_fields=["balance"])

            cart.clear()
            messages.success(request, "Buyurtma qabul qilindi! Taxminiy yetkazish vaqtini \"Buyurtmalarim\" bo'limida ko'rishingiz mumkin.")
            return redirect("order_list")
    else:
        form = CheckoutForm(initial={"address": request.user.address})

    return render(request, "orders/checkout.html", {"form": form, "cart": cart})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items").select_related("refund_request")
    return render(request, "orders/order_list.html", {"orders": orders, "active": "orders"})


@login_required
@require_POST
def order_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if not order.can_cancel:
        messages.error(request, "Bu buyurtmani endi bekor qilib bo'lmaydi")
        return redirect("order_list")
    order.status = "bekor"
    order.save()
    if order.payment_method == "wallet":
        request.user.balance = request.user.balance + order.total_amount
        request.user.save(update_fields=["balance"])
        messages.success(request, f"Buyurtma bekor qilindi. {order.total_amount:.0f} so'm wallet balansingizga qaytarildi.")
    else:
        messages.success(request, "Buyurtma bekor qilindi")
    return redirect("order_list")
