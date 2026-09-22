from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from orders.models import Order

from .forms import RefundRequestForm


@login_required
def refund_create(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if not order.can_request_refund:
        messages.error(request, "Bu buyurtma uchun qaytarish so'rovi yuborib bo'lmaydi")
        return redirect("order_list")

    if request.method == "POST":
        form = RefundRequestForm(request.POST, request.FILES)
        if form.is_valid():
            refund = form.save(commit=False)
            refund.order = order
            refund.user = request.user
            refund.save()
            messages.success(request, "Qaytarish so'rovi yuborildi. Admin ko'rib chiqadi.")
            return redirect("order_list")
    else:
        form = RefundRequestForm()

    return render(request, "refunds/refund_form.html", {"form": form, "order": order})
