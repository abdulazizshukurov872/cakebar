from rest_framework import permissions, viewsets
from rest_framework.filters import SearchFilter

from catalog.models import Category, Product
from orders.models import Order

from .serializers import CategorySerializer, OrderSerializer, ProductSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter]
    search_fields = ["name", "name_ru", "name_en"]

    def get_queryset(self):
        qs = super().get_queryset()
        category_id = self.request.query_params.get("category")
        if category_id:
            qs = qs.filter(category_id=category_id)
        return qs


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only: browse your own order history and live status.

    Placing an order goes through the web checkout flow (cart, promo
    codes, loyalty points and payment-gateway redirects all live there),
    so this intentionally doesn't duplicate that logic.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")
