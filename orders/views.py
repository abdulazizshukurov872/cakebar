from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from accounts.models import Address
from catalog.models import Product
from notifications.services import notify
from promotions.models import PromoCode

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

    addresses = Address.objects.filter(user=request.user)

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            for line in cart:
                if line["qty"] > line["product"].stock_quantity:
                    messages.error(
                        request,
                        f"\"{line['product'].name}\" dan faqat {line['product'].stock_quantity} dona qoldi. "
                        f"Savatdagi miqdorni kamaytiring.",
                    )
                    return render(request, "orders/checkout.html", {"form": form, "cart": cart, "addresses": addresses})

            subtotal = cart.get_total_price()
            payment_method = form.cleaned_data["payment_method"]
            promo_code_str = form.cleaned_data.get("promo_code", "").strip().upper()
            use_points = form.cleaned_data.get("use_points")

            promo = None
            discount_amount = 0
            if promo_code_str:
                promo = PromoCode.objects.filter(code=promo_code_str).first()
                if not promo or not promo.is_valid():
                    messages.error(request, "Promo-kod yaroqsiz yoki muddati o'tgan")
                    return render(request, "orders/checkout.html", {"form": form, "cart": cart, "addresses": addresses})
                discount_amount = subtotal * promo.discount_percent // 100

            after_promo = max(0, subtotal - discount_amount)

            points_used = 0
            points_discount = 0
            if use_points and request.user.loyalty_points > 0:
                max_points_value = request.user.loyalty_points * Order.POINT_VALUE
                points_discount = min(max_points_value, after_promo)
                points_used = int(points_discount // Order.POINT_VALUE)
                points_discount = points_used * Order.POINT_VALUE

            total = max(0, after_promo - points_discount)

            if payment_method == "wallet" and request.user.balance < total:
                messages.error(request, f"Wallet balansingizda yetarli mablag' yo'q ({request.user.balance:.0f} so'm). Boshqa to'lov usulini tanlang.")
                return render(request, "orders/checkout.html", {"form": form, "cart": cart, "addresses": addresses})

            order = form.save(commit=False)
            order.user = request.user
            order.total_amount = total
            order.discount_amount = discount_amount + points_discount
            order.promo_code = promo_code_str if promo else ""
            order.points_used = points_used
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
                line["product"].reduce_stock(line["qty"])

            if payment_method == "wallet":
                request.user.balance = request.user.balance - total
                request.user.save(update_fields=["balance"])
            if points_used:
                request.user.loyalty_points -= points_used
                request.user.save(update_fields=["loyalty_points"])
            if promo:
                promo.used_count += 1
                promo.save(update_fields=["used_count"])

            cart.clear()
            notify(request.user, "Buyurtma qabul qilindi", f"Buyurtma #{order.id} qabul qilindi, {total:.0f} so'm.", link="/my-orders/")
            messages.success(request, "Buyurtma qabul qilindi! Taxminiy yetkazish vaqtini \"Buyurtmalarim\" bo'limida ko'rishingiz mumkin.")
            return redirect("order_list")
    else:
        initial_address = addresses.filter(is_default=True).first()
        form = CheckoutForm(initial={"address": initial_address.address_line if initial_address else request.user.address})

    return render(request, "orders/checkout.html", {"form": form, "cart": cart, "addresses": addresses})


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
    for item in order.items.select_related("product"):
        if item.product:
            item.product.stock_quantity += item.quantity
            item.product.in_stock = True
            item.product.save(update_fields=["stock_quantity", "in_stock"])
    if order.points_used:
        request.user.loyalty_points += order.points_used
        request.user.save(update_fields=["loyalty_points"])
    if order.payment_method == "wallet":
        request.user.balance = request.user.balance + order.total_amount
        request.user.save(update_fields=["balance"])
        messages.success(request, f"Buyurtma bekor qilindi. {order.total_amount:.0f} so'm wallet balansingizga qaytarildi.")
    else:
        messages.success(request, "Buyurtma bekor qilindi")
    return redirect("order_list")


@login_required
@require_POST
def order_reorder(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    cart = Cart(request)
    added, skipped = 0, 0
    for item in order.items.select_related("product"):
        if item.product and item.product.in_stock:
            cart.add(item.product.id, item.quantity)
            added += 1
        else:
            skipped += 1
    if added:
        messages.success(request, f"{added} ta mahsulot savatga qo'shildi." + (f" {skipped} ta mahsulot endi mavjud emas." if skipped else ""))
        return redirect("cart_detail")
    messages.error(request, "Bu buyurtmadagi mahsulotlar endi mavjud emas")
    return redirect("order_list")
