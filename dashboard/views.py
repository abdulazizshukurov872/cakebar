from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.models import User
from catalog.models import Favorite, Product
from orders.models import Order
from refunds.models import RefundRequest


@login_required
def role_redirect(request):
    if request.user.is_staff:
        return redirect("admin_dashboard")
    return redirect("account_home")


@staff_member_required
def admin_dashboard(request):
    orders = Order.objects.all()
    refunds = RefundRequest.objects.all()
    total_sales = sum((o.total_amount for o in orders.exclude(status="bekor")), 0)
    pending_refunds = refunds.filter(status="kutilmoqda").count()
    refunded_count = refunds.filter(status="tasdiqlandi").count()
    refund_rate = round((refunded_count / orders.count()) * 100, 1) if orders.count() else 0

    context = {
        "total_sales": total_sales,
        "orders_count": orders.count(),
        "pending_refunds": pending_refunds,
        "refund_rate": refund_rate,
        "users_count": User.objects.filter(is_staff=False).count(),
        "products_count": Product.objects.count(),
        "recent_orders": orders[:8],
        "recent_refunds": refunds[:5],
    }
    return render(request, "dashboard/admin_dashboard.html", context)


@login_required
def account_home(request):
    if request.user.is_staff:
        messages.info(request, "Siz ADMIN sifatida kirdingiz — admin panelga yo'naltirildingiz.")
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
