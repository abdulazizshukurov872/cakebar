from rest_framework import serializers

from catalog.models import Category, Product
from orders.models import Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "name_ru", "name_en", "parent")


class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = (
            "id", "name", "name_ru", "name_en", "description", "composition",
            "quantity", "image", "category", "category_name", "price",
            "discount_price", "current_price", "in_stock", "stock_quantity",
            "rating", "calories",
        )

    def get_image(self, obj):
        request = self.context.get("request")
        image = obj.display_image
        if image and request:
            return request.build_absolute_uri(image) if image.startswith("/") else image
        return image


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("id", "product", "product_name", "price", "quantity", "line_total")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id", "address", "latitude", "longitude", "payment_method", "status",
            "total_amount", "promo_code", "discount_amount", "created_at",
            "estimated_delivery_at", "courier_name", "courier_phone", "items",
        )
        read_only_fields = (
            "status", "total_amount", "discount_amount", "created_at",
            "estimated_delivery_at", "courier_name", "courier_phone",
        )
