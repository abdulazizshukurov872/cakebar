import hashlib
from decimal import Decimal

from django.conf import settings

from catalog.models import Product

CART_SESSION_KEY = "cart"
INSCRIPTION_MAX_LENGTH = 60


def line_key(product_id, weight="", inscription=""):
    """Same product with a different weight or inscription is a separate line."""
    if not weight and not inscription:
        return str(product_id)
    digest = hashlib.sha1(f"{weight}|{inscription}".encode()).hexdigest()[:8]
    return f"{product_id}-{digest}"


class Cart:
    """Session cart. Each line is stored as
    {"p": product_id, "q": qty, "w": weight_kg as str or "", "i": inscription}.
    """

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        # Carts saved before lines had options were {product_id: qty}.
        for key, value in list(cart.items()):
            if isinstance(value, int):
                cart[key] = {"p": int(key), "q": value, "w": "", "i": ""}
                self.session.modified = True
        self.cart = cart

    def save(self):
        self.session.modified = True

    def add(self, product_id, qty=1, weight="", inscription=""):
        inscription = (inscription or "").strip()[:INSCRIPTION_MAX_LENGTH]
        key = line_key(product_id, weight, inscription)
        line = self.cart.get(key)
        if line:
            line["q"] += qty
        else:
            line = self.cart[key] = {"p": int(product_id), "q": qty, "w": weight or "", "i": inscription}
        if line["q"] <= 0:
            del self.cart[key]
        self.save()

    def update(self, key, qty):
        if key not in self.cart:
            return
        if qty <= 0:
            del self.cart[key]
        else:
            self.cart[key]["q"] = qty
        self.save()

    def remove(self, key):
        if key in self.cart:
            del self.cart[key]
            self.save()

    def clear(self):
        self.session[CART_SESSION_KEY] = {}
        self.cart = self.session[CART_SESSION_KEY]
        self.save()

    def __iter__(self):
        product_ids = {line["p"] for line in self.cart.values()}
        products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}
        lines, stale = [], []
        for key, line in self.cart.items():
            product = products.get(line["p"])
            if product is None:
                stale.append(key)
                continue
            weight = line["w"] if product.sold_by_weight else ""
            inscription = line["i"] if product.allows_inscription else ""
            price = product.unit_price(weight or None)
            if inscription:
                price += Decimal(settings.INSCRIPTION_FEE)
            lines.append({
                "key": key,
                "product": product,
                "qty": line["q"],
                "weight": weight,
                "inscription": inscription,
                "price": price,
                "line_total": price * line["q"],
            })
        # Products deleted from the catalog since they were added.
        for key in stale:
            del self.cart[key]
        if stale:
            self.save()
        return iter(lines)

    def __len__(self):
        return sum(line["q"] for line in self.cart.values())

    def get_total_price(self):
        return sum((line["line_total"] for line in self), Decimal("0"))

    def quantity_by_product(self):
        totals = {}
        for line in self.cart.values():
            totals[line["p"]] = totals.get(line["p"], 0) + line["q"]
        return totals
