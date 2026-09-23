import datetime
from decimal import Decimal
from unittest import mock

from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from catalog.models import Category, Product
from payments.models import Payment
from promotions.models import PromoCode

from .admin import OrderAdmin
from .models import Courier, Order, OrderItem
from .services import expire_unpaid_orders

PRICING = dict(DELIVERY_FEE=15000, FREE_DELIVERY_FROM=200000, MIN_ORDER_AMOUNT=30000, INSCRIPTION_FEE=0)


def make_product(name="Napoleon", price=50000, stock=10, **extra):
    category, _ = Category.objects.get_or_create(name="Tortlar")
    return Product.objects.create(name=name, category=category, price=price, stock_quantity=stock, **extra)


def make_user(phone="+998901112233", **extra):
    return User.objects.create_user(username=phone, phone=phone, password="Str0ng-pass!", **extra)


def checkout_data(**overrides):
    tomorrow = timezone.localdate() + datetime.timedelta(days=1)
    data = {
        "address": "Toshkent, Chilonzor 5",
        "payment_method": "naqd",
        "delivery_date": tomorrow.isoformat(),
        "delivery_slot": "12-14",
    }
    data.update(overrides)
    return data


@override_settings(**PRICING)
class CheckoutTests(TestCase):
    def setUp(self):
        self.user = make_user(balance=Decimal("500000"))
        self.client.force_login(self.user)
        self.product = make_product(price=50000, stock=3)

    def add(self, product=None, qty=1, **extra):
        return self.client.post(reverse("cart_add", args=[(product or self.product).id]), {"qty": qty, **extra})

    def test_wallet_checkout_charges_once_and_reserves_stock(self):
        self.add(qty=2)
        resp = self.client.post(reverse("checkout"), checkout_data(payment_method="wallet"))
        self.assertRedirects(resp, reverse("order_list"), fetch_redirect_response=False)

        order = Order.objects.get()
        self.assertEqual(order.total_amount, Decimal("115000"))  # 2 x 50 000 + 15 000 delivery
        self.assertEqual(order.delivery_fee, Decimal("15000"))
        self.assertEqual(order.delivery_slot, "12-14")
        self.user.refresh_from_db()
        self.product.refresh_from_db()
        self.assertEqual(self.user.balance, Decimal("385000"))
        self.assertEqual(self.product.stock_quantity, 1)

    def test_free_delivery_above_threshold(self):
        big = make_product("Katta tort", price=250000)
        self.add(big)
        self.client.post(reverse("checkout"), checkout_data())
        self.assertEqual(Order.objects.get().delivery_fee, 0)

    def test_cannot_buy_more_than_stock(self):
        self.add(qty=5)
        self.client.post(reverse("checkout"), checkout_data())
        self.assertFalse(Order.objects.exists())
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 3)

    def test_minimum_order_amount(self):
        cheap = make_product("Pechenye", price=12000)
        self.add(cheap)
        self.client.post(reverse("checkout"), checkout_data())
        self.assertFalse(Order.objects.exists())

    def test_promo_code_max_uses_is_enforced(self):
        PromoCode.objects.create(code="ONCE", discount_percent=10, max_uses=1)
        self.add()
        self.client.post(reverse("checkout"), checkout_data(promo_code="once"))
        self.add()
        self.client.post(reverse("checkout"), checkout_data(promo_code="ONCE"))
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(PromoCode.objects.get().used_count, 1)
        self.assertEqual(Order.objects.get().discount_amount, Decimal("5000"))

    def test_past_delivery_slot_is_rejected(self):
        self.add()
        today = timezone.localdate().isoformat()
        with mock.patch("orders.forms.slot_is_available", return_value=False):
            resp = self.client.post(reverse("checkout"), checkout_data(delivery_date=today))
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Order.objects.exists())

    def test_weight_and_inscription_are_priced_and_saved(self):
        cake = make_product("Medovik", price=100000, sold_by_weight=True, allows_inscription=True)
        with self.settings(INSCRIPTION_FEE=10000):
            self.add(cake, weight="1.5", inscription="Tug'ilgan kuning bilan!")
            self.client.post(reverse("checkout"), checkout_data())
        item = OrderItem.objects.get()
        self.assertEqual(item.weight_kg, Decimal("1.5"))
        self.assertEqual(item.inscription, "Tug'ilgan kuning bilan!")
        self.assertEqual(item.price, Decimal("160000"))  # 1.5 kg x 100 000 + 10 000 inscription

    def test_invalid_weight_falls_back_to_default(self):
        cake = make_product("Medovik", price=100000, sold_by_weight=True)
        self.add(cake, weight="99")
        line = next(iter(self.client.session["cart"].values()))
        self.assertEqual(line["w"], "1")

    def test_cart_update_with_garbage_qty_does_not_crash(self):
        self.add()
        resp = self.client.post(reverse("cart_update", args=[str(self.product.id)]), {"qty": "abc"})
        self.assertEqual(resp.status_code, 302)

    def test_old_session_cart_format_still_works(self):
        session = self.client.session
        session["cart"] = {str(self.product.id): 2}
        session.save()
        resp = self.client.get(reverse("cart_detail"))
        self.assertContains(resp, "100000")

    def test_deleted_product_is_dropped_from_cart(self):
        gone = make_product("Eski", price=40000)
        self.add(gone)
        gone.delete()
        self.client.get(reverse("cart_detail"))
        self.assertEqual(self.client.session["cart"], {})


@override_settings(**PRICING)
class CancelTests(TestCase):
    def setUp(self):
        self.user = make_user(balance=Decimal("0"), loyalty_points=0)
        self.product = make_product(stock=5)

    def make_order(self, **extra):
        defaults = dict(user=self.user, address="x", total_amount=Decimal("65000"), payment_method="wallet")
        defaults.update(extra)
        order = Order.objects.create(**defaults)
        OrderItem.objects.create(order=order, product=self.product, product_name="Napoleon", price=50000, quantity=2)
        return order

    def test_cancel_returns_money_stock_points_and_promo(self):
        PromoCode.objects.create(code="X", discount_percent=10, used_count=1)
        order = self.make_order(points_used=30, promo_code="X")
        refunded = order.cancel()
        self.assertEqual(refunded, Decimal("65000"))
        self.user.refresh_from_db()
        self.product.refresh_from_db()
        self.assertEqual(self.user.balance, Decimal("65000"))
        self.assertEqual(self.user.loyalty_points, 30)
        self.assertEqual(self.product.stock_quantity, 7)
        self.assertEqual(PromoCode.objects.get().used_count, 0)

    def test_cancel_twice_refunds_once(self):
        order = self.make_order()
        order.cancel()
        self.assertIsNone(Order.objects.get(pk=order.pk).cancel())
        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, Decimal("65000"))

    def test_customer_cancelling_paid_card_order_gets_money_back(self):
        order = self.make_order(payment_method="karta", status="tasdiqlangan")
        Payment.objects.create(order=order, provider="payme", amount=order.total_amount, state="performed")
        self.client.force_login(self.user)
        self.client.post(reverse("order_cancel", args=[order.id]))
        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, Decimal("65000"))

    def test_cash_order_cancel_credits_nothing(self):
        order = self.make_order(payment_method="naqd")
        self.assertEqual(order.cancel(), 0)
        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, 0)

    def test_admin_status_change_to_bekor_runs_full_cancel(self):
        order = self.make_order()
        admin_user = User.objects.create_superuser("admin", password="Adm1n-pass!")
        request = RequestFactory().post("/")
        request.user = admin_user
        request._messages = mock.MagicMock()
        order.status = "bekor"
        OrderAdmin(Order, AdminSite()).save_model(request, order, form=None, change=True)
        self.product.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 7)
        self.assertEqual(self.user.balance, Decimal("65000"))

    def test_delivered_order_cannot_be_cancelled(self):
        order = self.make_order(status="yetkazildi")
        with self.assertRaises(ValueError):
            order.cancel()


@override_settings(**PRICING, UNPAID_ORDER_TTL_MINUTES=30)
class ExpireUnpaidTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.product = make_product(stock=5)

    def card_order(self, minutes_ago, provider_tx=""):
        order = Order.objects.create(user=self.user, address="x", total_amount=50000, payment_method="karta")
        Order.objects.filter(pk=order.pk).update(created_at=timezone.now() - datetime.timedelta(minutes=minutes_ago))
        OrderItem.objects.create(order=order, product=self.product, product_name="N", price=50000, quantity=1)
        Payment.objects.create(order=order, provider="payme", amount=50000, provider_transaction_id=provider_tx)
        return order

    def test_expires_old_unpaid_and_releases_stock(self):
        old = self.card_order(minutes_ago=45)
        fresh = self.card_order(minutes_ago=5)
        in_progress = self.card_order(minutes_ago=45, provider_tx="payme-123")
        demo = Order.objects.create(user=self.user, address="x", total_amount=50000, payment_method="karta")

        self.assertEqual(expire_unpaid_orders(), [old.pk])
        self.assertEqual(Order.objects.get(pk=old.pk).status, "bekor")
        self.assertEqual(Payment.objects.get(order=old).state, "cancelled")
        for order in (fresh, in_progress, demo):
            self.assertEqual(Order.objects.get(pk=order.pk).status, "yangi")
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 6)


class DeliveryTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.courier_user = make_user("+998907778899")
        self.courier = Courier.objects.create(user=self.courier_user, name="Aziz", phone="+998901234567")

    def test_points_awarded_once_and_courier_assigned(self):
        order = Order.objects.create(user=self.user, address="x", total_amount=Decimal("120000"))
        order.status = "tasdiqlangan"
        order.save()
        self.assertEqual(order.courier, self.courier)
        order.status = "yetkazildi"
        order.save()
        order.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.loyalty_points, 120)

    def test_courier_panel_marks_delivered(self):
        order = Order.objects.create(user=self.user, address="x", total_amount=50000, status="yetkazilmoqda", courier=self.courier)
        self.client.force_login(self.courier_user)
        self.assertContains(self.client.get(reverse("courier_panel")), f"№ {order.id}")
        self.client.post(reverse("courier_update_status", args=[order.id]), {"status": "yetkazildi"})
        self.assertEqual(Order.objects.get(pk=order.pk).status, "yetkazildi")

    def test_courier_cannot_skip_steps_or_touch_others(self):
        order = Order.objects.create(user=self.user, address="x", total_amount=50000, status="tasdiqlangan", courier=self.courier)
        self.client.force_login(self.courier_user)
        self.client.post(reverse("courier_update_status", args=[order.id]), {"status": "yetkazildi"})
        self.assertEqual(Order.objects.get(pk=order.pk).status, "tasdiqlangan")

        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("courier_panel")).status_code, 404)
