"""Checkout: turns a cart into an order.

Everything that moves money or stock happens inside one transaction with the
product, user and promo-code rows locked, so two simultaneous checkouts can't
both spend the same wallet balance, sell the last cake twice, or push a promo
code past its max_uses.
"""
import datetime
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from accounts.models import User
from catalog.models import Product
from promotions.models import PromoCode

from .models import Order, OrderItem


class CheckoutError(Exception):
    pass


def delivery_fee_for(amount):
    if settings.FREE_DELIVERY_FROM and amount >= settings.FREE_DELIVERY_FROM:
        return Decimal("0")
    return Decimal(settings.DELIVERY_FEE)


def price_summary(subtotal):
    """Delivery fee / minimum-order info shown on the cart and checkout pages."""
    fee = delivery_fee_for(subtotal)
    return {
        "subtotal": subtotal,
        "delivery_fee": fee,
        "total": subtotal + fee,
        "min_order_amount": settings.MIN_ORDER_AMOUNT,
        "below_minimum": subtotal < settings.MIN_ORDER_AMOUNT,
        "missing_for_minimum": max(Decimal("0"), Decimal(settings.MIN_ORDER_AMOUNT) - subtotal),
        "free_delivery_from": settings.FREE_DELIVERY_FROM,
        "missing_for_free_delivery": max(Decimal("0"), Decimal(settings.FREE_DELIVERY_FROM) - subtotal) if settings.FREE_DELIVERY_FROM else 0,
    }


def place_order(user, cart, data):
    """Create the order from the cart. `data` is CheckoutForm.cleaned_data.
    Raises CheckoutError with a user-facing message when something is off."""
    lines = list(cart)
    if not lines:
        raise CheckoutError("Savat bo'sh — avval mahsulot tanlang")

    subtotal = sum((line["line_total"] for line in lines), Decimal("0"))
    if subtotal < settings.MIN_ORDER_AMOUNT:
        raise CheckoutError(f"Minimal buyurtma summasi {settings.MIN_ORDER_AMOUNT:,} so'm.".replace(",", " "))

    payment_method = data["payment_method"]
    promo_code_str = (data.get("promo_code") or "").strip().upper()

    with transaction.atomic():
        products = Product.objects.select_for_update().in_bulk({line["product"].id for line in lines})
        wanted = {}
        for line in lines:
            wanted[line["product"].id] = wanted.get(line["product"].id, 0) + line["qty"]
        for product_id, qty in wanted.items():
            product = products.get(product_id)
            if product is None:
                raise CheckoutError("Savatdagi mahsulotlardan biri endi mavjud emas.")
            if qty > product.stock_quantity:
                raise CheckoutError(
                    f"\"{product.name}\" dan faqat {product.stock_quantity} dona qoldi. Savatdagi miqdorni kamaytiring."
                )

        locked_user = User.objects.select_for_update().get(pk=user.pk)

        promo = None
        discount_amount = Decimal("0")
        if promo_code_str:
            promo = PromoCode.objects.select_for_update().filter(code=promo_code_str).first()
            if not promo or not promo.is_valid():
                raise CheckoutError("Promo-kod yaroqsiz yoki muddati o'tgan")
            discount_amount = subtotal * promo.discount_percent // 100
        after_promo = max(Decimal("0"), subtotal - discount_amount)

        points_used = 0
        points_discount = Decimal("0")
        if data.get("use_points") and locked_user.loyalty_points > 0:
            max_points_value = locked_user.loyalty_points * Order.POINT_VALUE
            points_used = int(min(max_points_value, after_promo) // Order.POINT_VALUE)
            points_discount = Decimal(points_used * Order.POINT_VALUE)

        delivery_fee = delivery_fee_for(after_promo)
        total = max(Decimal("0"), after_promo - points_discount) + delivery_fee

        if payment_method == "wallet" and locked_user.balance < total:
            raise CheckoutError(
                f"Wallet balansingizda yetarli mablag' yo'q ({locked_user.balance:.0f} so'm). Boshqa to'lov usulini tanlang."
            )

        order = Order.objects.create(
            user=locked_user,
            address=data["address"],
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            payment_method=payment_method,
            delivery_date=data.get("delivery_date"),
            delivery_slot=data.get("delivery_slot") or "",
            total_amount=total,
            delivery_fee=delivery_fee,
            discount_amount=discount_amount + points_discount,
            promo_code=promo.code if promo else "",
            points_used=points_used,
        )
        OrderItem.objects.bulk_create([
            OrderItem(
                order=order,
                product=line["product"],
                product_name=line["product"].name,
                image_url=line["product"].image_url,
                price=line["price"],
                quantity=line["qty"],
                weight_kg=Decimal(line["weight"]) if line["weight"] else None,
                inscription=line["inscription"],
            )
            for line in lines
        ])
        for product_id, qty in wanted.items():
            remaining = products[product_id].stock_quantity - qty
            Product.objects.filter(pk=product_id).update(
                stock_quantity=F("stock_quantity") - qty, in_stock=remaining > 0,
            )

        user_updates = {}
        if payment_method == "wallet":
            user_updates["balance"] = F("balance") - total
        if points_used:
            user_updates["loyalty_points"] = F("loyalty_points") - points_used
        if user_updates:
            User.objects.filter(pk=user.pk).update(**user_updates)
        if promo:
            PromoCode.objects.filter(pk=promo.pk).update(used_count=F("used_count") + 1)

    cart.clear()
    return order


def expire_unpaid_orders(now=None):
    """Cancel card orders whose online payment was never completed, so the
    stock they reserved goes back on sale.

    - No payment started at the provider: expire after UNPAID_ORDER_TTL_MINUTES.
    - Payment started (provider transaction exists): give it Payme's 12h
      transaction window before expiring.
    Orders without a Payment row are demo-mode card orders and are left alone.
    """
    now = now or timezone.now()
    short_cutoff = now - datetime.timedelta(minutes=settings.UNPAID_ORDER_TTL_MINUTES)
    long_cutoff = now - datetime.timedelta(hours=12)
    candidates = Order.objects.filter(
        status="yangi", payment_method="karta", payment__state="created",
    ).select_related("payment")
    expired = []
    for order in candidates.filter(created_at__lt=short_cutoff):
        started = bool(order.payment.provider_transaction_id)
        if started and order.created_at >= long_cutoff:
            continue
        if order.cancel(refund_money=False, reason="to'lov o'z vaqtida amalga oshirilmadi") is not None:
            # A late PerformTransaction/Complete for this payment must now be refused.
            type(order.payment).objects.filter(pk=order.payment.pk, state="created").update(
                state="cancelled", cancelled_at=now, error_reason="Muddati o'tdi (to'lanmagan)",
            )
            expired.append(order.pk)
    return expired
