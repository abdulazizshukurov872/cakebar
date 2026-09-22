from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from catalog.models import Product
from orders.models import OrderItem

from .forms import ReviewForm
from .models import Review


@login_required
@require_POST
def review_create(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    can_review = OrderItem.objects.filter(
        order__user=request.user, order__status="yetkazildi", product=product,
    ).exists()
    if not can_review:
        messages.error(request, "Sharh qoldirish uchun avval shu mahsulotni xarid qilib, yetkazib olishingiz kerak.")
        return redirect("product_detail", product_id=product.id)

    existing = Review.objects.filter(product=product, user=request.user).first()
    form = ReviewForm(request.POST, instance=existing)
    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.save()
        messages.success(request, "Sharhingiz uchun rahmat!")
    else:
        messages.error(request, "Baho tanlanmadi yoki xato yuz berdi.")
    return redirect("product_detail", product_id=product.id)
