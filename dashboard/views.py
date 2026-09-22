import csv
import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, F, Sum
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from accounts.models import User
from catalog.models import Favorite, Product
from orders.models import Order, OrderItem
from refunds.models import RefundRequest

superadmin_required = user_passes_test(lambda u: u.is_active and u.is_superuser, login_url="login")


@login_required
def role_redirect(request):
    if request.user.is_superuser:
        return redirect("admin_dashboard")
    return redirect("account_home")


@superadmin_required
def admin_dashboard(request):
    orders = Order.objects.all()
    refunds = RefundRequest.objects.all()
    paid_orders = orders.exclude(status="bekor")
    total_sales = sum((o.total_amount for o in paid_orders), 0)
    pending_refunds = refunds.filter(status="kutilmoqda").count()
    new_orders = orders.filter(status="yangi").count()
    refunded_count = refunds.filter(status="tasdiqlandi").count()
    refund_rate = round((refunded_count / orders.count()) * 100, 1) if orders.count() else 0

    # --- last-7-days sales, one bar per day (magnitude, single series) ---
    today = timezone.localdate()
    days = [today - datetime.timedelta(days=i) for i in range(6, -1, -1)]
    by_day = dict(
        paid_orders.filter(created_at__date__gte=days[0])
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total=Sum("total_amount"))
        .values_list("day", "total")
    )
    sales_by_day = [{"label": d.strftime("%d.%m"), "value": float(by_day.get(d, 0) or 0)} for d in days]
    max_day_value = max((d["value"] for d in sales_by_day), default=0) or 1
    for d in sales_by_day:
        d["pct"] = round(d["value"] / max_day_value * 100, 1)
        d["peak"] = d["value"] == max_day_value and d["value"] > 0

    # --- top 5 products by quantity sold (magnitude ranking) ---
    top_products = (
        OrderItem.objects.exclude(order__status="bekor")
        .values("product_name")
        .annotate(qty=Sum("quantity"), revenue=Sum(F("price") * F("quantity")))
        .order_by("-qty")[:5]
    )
    top_products = list(top_products)
    max_qty = max((p["qty"] for p in top_products), default=0) or 1
    for p in top_products:
        p["pct"] = round(p["qty"] / max_qty * 100, 1)

    # --- revenue by category, top 6 (magnitude ranking) ---
    by_category = (
        OrderItem.objects.exclude(order__status="bekor")
        .values(cat=F("product__category__name"))
        .annotate(revenue=Sum(F("price") * F("quantity")))
        .order_by("-revenue")[:6]
    )
    by_category = list(by_category)
    max_cat_revenue = max((c["revenue"] for c in by_category), default=0) or 1
    for c in by_category:
        c["pct"] = round(c["revenue"] / max_cat_revenue * 100, 1)

    low_stock = Product.objects.filter(in_stock=False)[:6]

    # --- top 5 customers by spend (magnitude ranking) ---
    top_customers = (
        paid_orders.values("user__id", "user__username", "user__phone")
        .annotate(total=Sum("total_amount"), orders=Count("id"))
        .order_by("-total")[:5]
    )
    top_customers = list(top_customers)
    max_customer_total = max((c["total"] for c in top_customers), default=0) or 1
    for c in top_customers:
        c["pct"] = round(c["total"] / max_customer_total * 100, 1)

    context = {
        "total_sales": total_sales,
        "orders_count": orders.count(),
        "pending_refunds": pending_refunds,
        "new_orders": new_orders,
        "refund_rate": refund_rate,
        "users_count": User.objects.filter(is_superuser=False).count(),
        "products_count": Product.objects.count(),
        "recent_orders": orders[:8],
        "recent_refunds": refunds[:5],
        "sales_by_day": sales_by_day,
        "top_products": top_products,
        "by_category": by_category,
        "low_stock": low_stock,
        "low_stock_count": Product.objects.filter(in_stock=False).count(),
        "top_customers": top_customers,
    }
    return render(request, "dashboard/admin_dashboard.html", context)


@superadmin_required
def export_orders_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="cakebar-buyurtmalar-{timezone.localdate()}.csv"'
    writer = csv.writer(response)
    writer.writerow(["ID", "Mijoz", "Telefon", "Manzil", "To'lov usuli", "Status", "Summa", "Promo-kod", "Chegirma", "Yaratilgan sana"])
    for o in Order.objects.select_related("user").order_by("-created_at"):
        writer.writerow([
            o.id, o.user.get_full_name() or o.user.username, o.user.phone, o.address,
            o.get_payment_method_display(), o.get_status_display(), o.total_amount,
            o.promo_code, o.discount_amount, o.created_at.strftime("%Y-%m-%d %H:%M"),
        ])
    return response


@login_required
def account_home(request):
    if request.user.is_superuser:
        messages.info(request, "Siz SUPERADMIN sifatida kirdingiz — admin panelga yo'naltirildingiz.")
        return redirect("admin_dashboard")
    orders = Order.objects.filter(user=request.user)[:5]
    favorites_count = Favorite.objects.filter(user=request.user).count()
    context = {
        "orders": orders,
        "orders_count": Order.objects.filter(user=request.user).count(),
        "favorites_count": favorites_count,
        "pending_refunds": RefundRequest.objects.filter(user=request.user, status="kutilmoqda").count(),
        "active": "account",
    }
    return render(request, "dashboard/account_home.html", context)
