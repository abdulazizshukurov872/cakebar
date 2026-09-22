from decimal import Decimal

from catalog.models import Product

CART_SESSION_KEY = "cart"


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def save(self):
        self.session.modified = True

    def add(self, product_id, qty=1):
        pid = str(product_id)
        if pid in self.cart:
            self.cart[pid] += qty
        else:
            self.cart[pid] = qty
        if self.cart[pid] <= 0:
            del self.cart[pid]
        self.save()

    def update(self, product_id, qty):
        pid = str(product_id)
        if qty <= 0:
            self.cart.pop(pid, None)
        else:
            self.cart[pid] = qty
        self.save()

    def remove(self, product_id):
        pid = str(product_id)
        if pid in self.cart:
            del self.cart[pid]
            self.save()

    def clear(self):
        self.session[CART_SESSION_KEY] = {}
        self.save()

    def __iter__(self):
        products = Product.objects.filter(id__in=self.cart.keys())
        for product in products:
            qty = self.cart[str(product.id)]
            price = product.current_price
            yield {
                "product": product,
                "qty": qty,
                "price": price,
                "line_total": price * qty,
            }

    def __len__(self):
        return sum(self.cart.values())

    def get_total_price(self):
        return sum((line["line_total"] for line in self), Decimal("0"))
