from unittest import mock

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from orders.tests import make_user

from .models import User


class SignupTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_weak_password_is_rejected(self):
        resp = self.client.post(reverse("signup"), {"phone": "+998901234567", "password": "1234"})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.exists())
        self.assertContains(resp, "kamida 8 belgi")

    def test_signup_without_sms_provider_creates_account(self):
        with mock.patch("notifications.eskiz.is_configured", return_value=False):
            resp = self.client.post(reverse("signup"), {"phone": "+998901234567", "password": "Shirin-tort-2026"})
        self.assertEqual(resp.status_code, 200)
        user = User.objects.get()
        self.assertFalse(user.phone_verified)

    @override_settings(PHONE_VERIFICATION=True)
    def test_signup_requires_sms_code_when_provider_configured(self):
        sent = {}

        def fake_send(phone, text):
            sent["code"] = text.split(": ")[1][:6]
            return True

        with mock.patch("notifications.eskiz.is_configured", return_value=True), \
                mock.patch("notifications.eskiz.send_sms", side_effect=fake_send):
            resp = self.client.post(reverse("signup"), {"phone": "+998901234567", "password": "Shirin-tort-2026"})
            self.assertRedirects(resp, reverse("signup_verify"))
            self.assertFalse(User.objects.exists())

            self.client.post(reverse("signup_verify"), {"code": "000000" if sent["code"] != "000000" else "111111"})
            self.assertFalse(User.objects.exists())

            self.client.post(reverse("signup_verify"), {"code": sent["code"]})
        user = User.objects.get()
        self.assertTrue(user.phone_verified)
        self.assertTrue(user.check_password("Shirin-tort-2026"))


@override_settings(LOGIN_RATE_LIMIT=3)
class LoginRateLimitTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = make_user()

    def login(self, password):
        return self.client.post(reverse("login"), {"username": self.user.username, "password": password})

    def test_locked_out_after_repeated_failures_even_with_right_password(self):
        for _ in range(3):
            self.login("wrong")
        resp = self.login("Str0ng-pass!")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Juda ko&#x27;p urinish")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_successful_login_resets_counter(self):
        self.login("wrong")
        self.login("wrong")
        self.assertEqual(self.login("Str0ng-pass!").status_code, 302)
        self.client.logout()
        self.login("wrong")
        self.assertEqual(self.login("Str0ng-pass!").status_code, 302)
