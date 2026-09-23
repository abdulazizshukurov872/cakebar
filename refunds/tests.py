from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from orders.models import Order
from orders.tests import make_user

from .models import RefundRequest


class RefundApproveTests(TestCase):
    def setUp(self):
        self.user = make_user(balance=Decimal("0"), loyalty_points=0)

    def make_refund(self, payment_method):
        order = Order.objects.create(
            user=self.user, address="x", total_amount=Decimal("80000"),
            payment_method=payment_method, status="yetkazildi", delivered_at=timezone.now(),
        )
        return RefundRequest.objects.create(order=order, user=self.user, reason="buzilgan")

    def test_every_payment_method_is_refunded_to_wallet(self):
        for method in ("naqd", "wallet", "karta"):
            with self.subTest(method=method):
                self.user.balance = 0
                self.user.save()
                refund = self.make_refund(method)
                refund.approve(refund.order.total_amount)
                self.user.refresh_from_db()
                self.assertEqual(self.user.balance, Decimal("80000"))
                refund.order.delete()

    def test_approving_twice_pays_once(self):
        refund = self.make_refund("wallet")
        self.assertTrue(refund.approve(Decimal("80000")))
        self.assertFalse(RefundRequest.objects.get(pk=refund.pk).approve(Decimal("80000")))
        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, Decimal("80000"))

    def test_amount_is_capped_and_earned_points_taken_back(self):
        refund = self.make_refund("naqd")
        Order.objects.filter(pk=refund.order.pk).update(points_earned=80)
        self.user.loyalty_points = 100
        self.user.save()
        refund = RefundRequest.objects.get(pk=refund.pk)
        refund.approve(Decimal("999999"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, Decimal("80000"))
        self.assertEqual(self.user.loyalty_points, 20)
        self.assertEqual(refund.order.status, "qaytarildi")

    def test_rejected_refund_cannot_be_approved_later(self):
        refund = self.make_refund("wallet")
        refund.reject("Rasm yo'q")
        self.assertFalse(RefundRequest.objects.get(pk=refund.pk).approve(Decimal("80000")))
        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, 0)
