from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from accounts.models import Address
from catalog.models import Product
from notifications import telegram
from notifications.services import notify
from payments import click, payme
from payments.models import Payment

from .cart import Cart
from .forms import CheckoutForm
from .models import Order
from .services import CheckoutError, place_order, price_summary


def _parse_qty(value, default=1):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def cart_detail(request):
    cart = Cart(request)
    return render(request, "orders/cart.html", {"cart": cart, "summary": price_summary(cart.get_total_price())})


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, in_stock=True)
    weight = ""
    if product.sold_by_weight:
        weight = request.POST.get("weight", Product.WEIGHT_OPTIONS[0])
        if weight not in Product.WEIGHT_OPTIONS:
            weight = Product.WEIGHT_OPTIONS[0]
    inscription = request.POST.get("inscription", "") if product.allows_inscription else ""
    qty = max(1, min(_parse_qty(request.POST.get("qty")), 50))
    Cart(request).add(product.id, qty, weight=weight, inscription=inscription)
    messages.success(request, "Savatga qo'shildi")
    next_url = request.POST.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect("product_list")


@require_POST
def cart_update(request, key):
    qty = _parse_qty(request.POST.get("qty"), default=None)
    if qty is not None:
        Cart(request).update(key, min(qty, 50))
    return redirect("cart_detail")


@require_POST
def cart_remove(request, key):
    Cart(request).remove(key)
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
    summary = price_summary(cart.get_total_price())

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                order = place_order(request.user, cart, form.cleaned_data)
            except CheckoutError as exc:
                messages.error(request, str(exc))
            else:
                return _after_order_placed(request, order)
    else:
        initial_address = addresses.filter(is_default=True).first()
        form = CheckoutForm(initial={"address": initial_address.address_line if initial_address else request.user.address})

    return render(request, "orders/checkout.html", {"form": form, "cart": cart, "addresses": addresses, "summary": summary})


def _after_order_placed(request, order):
    total = order.total_amount
    telegram.notify_admins(_admin_order_text(order))

    if order.payment_method == "karta" and (payme.is_configured() or click.is_configured()):
        provider = "payme" if payme.is_configured() else "click"
        Payment.objects.get_or_create(order=order, defaults={"provider": provider, "amount": total})
        checkout_url = payme.build_checkout_url(order) if provider == "payme" else click.build_checkout_url(order)
        notify(request.user, "Buyurtma qabul qilindi", f"Buyurtma #{order.id} to'lov kutilmoqda, {total:.0f} so'm.", link="/my-orders/")
        messages.info(request, "Buyurtmangiz qabul qilindi. To'lovni yakunlash uchun to'lov tizimiga yo'naltirilyapsiz.")
        return redirect(checkout_url)

    notify(request.user, "Buyurtma qabul qilindi", f"Buyurtma #{order.id} qabul qilindi, {total:.0f} so'm.", link="/my-orders/")
    messages.success(request, "Buyurtma qabul qilindi! Yetkazish vaqtini \"Buyurtmalarim\" bo'limida ko'rishingiz mumkin.")
    return redirect("order_list")


def _admin_order_text(order):
    lines = [f"🆕 Yangi buyurtma #{order.id}", f"Mijoz: {order.user.get_full_name() or order.user.phone or order.user.username}"]
    if order.user.phone:
        lines.append(f"Tel: {order.user.phone}")
    lines.append(f"Manzil: {order.address}")
    if order.delivery_date:
        lines.append(f"Yetkazish: {order.delivery_date:%d.%m} {order.get_delivery_slot_display()}")
    for item in order.items.all():
        extra = []
        if item.weight_kg:
            extra.append(f"{item.weight_kg} kg")
        if item.inscription:
            extra.append(f"yozuv: «{item.inscription}»")
        lines.append(f"• {item.product_name} x{item.quantity}" + (f" ({', '.join(extra)})" if extra else ""))
    lines.append(f"Jami: {order.total_amount:.0f} so'm — {order.get_payment_method_display()}")
    return "\n".join(lines)


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items").select_related("refund_request")
    return render(request, "orders/order_list.html", {"orders": orders, "active": "orders"})


@login_required
def order_status_json(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return JsonResponse({
        "status": order.status,
        "status_display": order.get_status_display(),
        "status_step_index": order.status_step_index,
        "courier_name": order.courier_name,
        "courier_phone": order.courier_phone,
        "estimated_delivery_at": order.estimated_delivery_at.isoformat() if order.estimated_delivery_at else None,
        "delivered_at": order.delivered_at.isoformat() if order.delivered_at else None,
    })


@login_required
@require_POST
def order_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if not order.can_cancel:
        messages.error(request, "Bu buyurtmani endi bekor qilib bo'lmaydi")
        return redirect("order_list")
    refunded = order.cancel()
    if refunded:
        messages.success(request, f"Buyurtma bekor qilindi. {refunded:.0f} so'm wallet balansingizga qaytarildi.")
    else:
        messages.success(request, "Buyurtma bekor qilindi")
    return redirect("order_list")


@login_required
def order_invoice_pdf(request, order_id):
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    order = get_object_or_404(Order.objects.prefetch_related("items"), id=order_id, user=request.user)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="cakebar-chek-{order.id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 30 * mm

    p.setFont("Helvetica-Bold", 18)
    p.drawString(20 * mm, y, "CakeBar")
    p.setFont("Helvetica", 10)
    y -= 8 * mm
    p.drawString(20 * mm, y, f"Buyurtma cheki #{order.id}")
    y -= 6 * mm
    p.drawString(20 * mm, y, f"Sana: {order.created_at.strftime('%d.%m.%Y %H:%M')}")
    y -= 6 * mm
    p.drawString(20 * mm, y, f"Mijoz: {order.user.get_full_name() or order.user.phone or order.user.username}")
    y -= 6 * mm
    p.drawString(20 * mm, y, f"Manzil: {order.address}")
    if order.delivery_date:
        y -= 6 * mm
        p.drawString(20 * mm, y, f"Yetkazish: {order.delivery_date.strftime('%d.%m.%Y')} {order.get_delivery_slot_display()}")
    y -= 6 * mm
    p.drawString(20 * mm, y, f"To'lov usuli: {order.get_payment_method_display()}")
    y -= 6 * mm
    p.drawString(20 * mm, y, f"Holati: {order.get_status_display()}")

    y -= 12 * mm
    p.setFont("Helvetica-Bold", 10)
    p.drawString(20 * mm, y, "Mahsulot")
    p.drawString(120 * mm, y, "Miqdor")
    p.drawString(145 * mm, y, "Narx")
    p.drawString(170 * mm, y, "Jami")
    y -= 4 * mm
    p.line(20 * mm, y, 190 * mm, y)
    y -= 6 * mm

    p.setFont("Helvetica", 10)
    for item in order.items.all():
        if y < 30 * mm:
            p.showPage()
            y = height - 30 * mm
        name = item.product_name
        if item.weight_kg:
            name += f" ({item.weight_kg} kg)"
        p.drawString(20 * mm, y, name[:45])
        p.drawString(120 * mm, y, str(item.quantity))
        p.drawRightString(165 * mm, y, f"{item.price:.0f}")
        p.drawRightString(190 * mm, y, f"{item.line_total:.0f}")
        if item.inscription:
            y -= 5 * mm
            p.setFont("Helvetica-Oblique", 9)
            p.drawString(24 * mm, y, f"Yozuv: {item.inscription}"[:60])
            p.setFont("Helvetica", 10)
        y -= 6 * mm

    y -= 4 * mm
    p.line(20 * mm, y, 190 * mm, y)
    y -= 8 * mm
    if order.discount_amount:
        p.drawRightString(190 * mm, y, f"Chegirma: -{order.discount_amount:.0f} so'm")
        y -= 6 * mm
    if order.delivery_fee:
        p.drawRightString(190 * mm, y, f"Yetkazish: {order.delivery_fee:.0f} so'm")
        y -= 6 * mm
    p.setFont("Helvetica-Bold", 12)
    p.drawRightString(190 * mm, y, f"Jami: {order.total_amount:.0f} so'm")

    p.showPage()
    p.save()
    return response


@login_required
@require_POST
def order_reorder(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    cart = Cart(request)
    added, skipped = 0, 0
    for item in order.items.select_related("product"):
        if item.product and item.product.in_stock:
            weight = ""
            if item.weight_kg:
                weight = f"{item.weight_kg.normalize():f}"
            cart.add(item.product.id, item.quantity, weight=weight, inscription=item.inscription)
            added += 1
        else:
            skipped += 1
    if added:
        messages.success(request, f"{added} ta mahsulot savatga qo'shildi." + (f" {skipped} ta mahsulot endi mavjud emas." if skipped else ""))
        return redirect("cart_detail")
    messages.error(request, "Bu buyurtmadagi mahsulotlar endi mavjud emas")
    return redirect("order_list")


# --- Courier panel ---------------------------------------------------------

def _courier_or_404(request):
    courier = getattr(request.user, "courier_profile", None)
    if courier is None or not courier.is_active:
        raise Http404("Siz kuryer sifatida ro'yxatdan o'tmagansiz")
    return courier


@login_required
def courier_panel(request):
    courier = _courier_or_404(request)
    active = courier.orders.filter(status__in=Order.ACTIVE_STATUSES).select_related("user").prefetch_related("items").order_by("delivery_date", "delivery_slot", "created_at")
    delivered = courier.orders.filter(status="yetkazildi").order_by("-delivered_at")[:10]
    return render(request, "orders/courier_panel.html", {"courier": courier, "active_orders": active, "delivered_orders": delivered})


@login_required
@require_POST
def courier_update_status(request, order_id):
    courier = _courier_or_404(request)
    order = get_object_or_404(Order, id=order_id, courier=courier)
    transitions = {"tasdiqlangan": "yetkazilmoqda", "tayyorlanmoqda": "yetkazilmoqda", "yetkazilmoqda": "yetkazildi"}
    new_status = request.POST.get("status")
    if transitions.get(order.status) != new_status:
        messages.error(request, "Bu holatga o'tkazib bo'lmaydi")
        return redirect("courier_panel")
    order.status = new_status
    order.save()
    messages.success(request, f"Buyurtma #{order.id}: {order.get_status_display()}")
    return redirect("courier_panel")
