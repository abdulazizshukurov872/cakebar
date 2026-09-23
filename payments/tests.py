import base64
import json
from decimal import Decimal

from django.test import TestCase, override_settings
from django.urls import reverse

from orders.models import Order, OrderItem
from orders.tests import make_product, make_user

from .models import Payment

PAYME = dict(PAYME_MERCHANT_ID="merchant", PAYME_KEY="secret-key")


@override_settings(**PAYME)
class PaymeWebhookTests(TestCase):
    def setUp(self):
        self.user = make_user(balance=Decimal("0"))
        self.product = make_product(stock=4)  # 1 of 5 already reserved by this order
        self.order = Order.objects.create(user=self.user, address="x", total_amount=Decimal("50000"), payment_method="karta")
        OrderItem.objects.create(order=self.order, product=self.product, product_name="N", price=50000, quantity=1)

    def rpc(self, method, params, key="secret-key"):
        auth = base64.b64encode(f"Paycom:{key}".encode()).decode()
        resp = self.client.post(
            reverse("payme_webhook"), json.dumps({"id": 1, "method": method, "params": params}),
            content_type="application/json", HTTP_AUTHORIZATION=f"Basic {auth}",
        )
        return resp.json()

    def account(self):
        return {"amount": 5000000, "account": {"order_id": self.order.id}}

    def test_wrong_key_is_rejected(self):
        self.assertEqual(self.rpc("CheckPerformTransaction", self.account(), key="nope")["error"]["code"], -32504)

    def test_cancelled_order_cannot_be_paid(self):
        self.order.cancel()
        self.assertEqual(self.rpc("CheckPerformTransaction", self.account())["error"]["code"], -31008)
        self.assertEqual(self.rpc("CreateTransaction", {**self.account(), "id": "t1", "time": 1})["error"]["code"], -31008)

    def test_full_payment_then_cancel_restores_stock_without_wallet_credit(self):
        self.assertTrue(self.rpc("CheckPerformTransaction", self.account())["result"]["allow"])
        self.rpc("CreateTransaction", {**self.account(), "id": "t1", "time": 1})
        self.assertEqual(self.rpc("PerformTransaction", {"id": "t1"})["result"]["state"], 2)
        self.assertEqual(Order.objects.get(pk=self.order.pk).status, "tasdiqlangan")

        result = self.rpc("CancelTransaction", {"id": "t1", "reason": 5})["result"]
        self.assertEqual(result["state"], -2)
        self.assertEqual(Order.objects.get(pk=self.order.pk).status, "bekor")
        self.product.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 5)
        self.assertEqual(self.user.balance, 0)  # Payme returns the money to the card itself

    def test_perform_after_order_expired_is_refused(self):
        self.rpc("CreateTransaction", {**self.account(), "id": "t1", "time": 1})
        self.order.cancel()
        self.assertEqual(self.rpc("PerformTransaction", {"id": "t1"})["error"]["code"], -31008)
        self.assertEqual(Payment.objects.get().state, "cancelled")
