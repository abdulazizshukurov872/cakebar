import hashlib
import hmac
import json
import time
from unittest import mock
from urllib.parse import urlencode

from django.test import TestCase, override_settings
from django.urls import reverse

from orders.tests import make_user

from . import telegram

TOKEN = "123456:TEST-TOKEN"


def signed_init_data(user_id, auth_date=None, token=TOKEN):
    fields = {
        "auth_date": str(auth_date or int(time.time())),
        "query_id": "AAE",
        "user": json.dumps({"id": user_id, "first_name": "Ali"}),
    }
    check = "\n".join(f"{k}={v}" for k, v in sorted(fields.items()))
    secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    fields["hash"] = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    return urlencode(fields)


@override_settings(TELEGRAM_BOT_TOKEN=TOKEN)
class MiniAppTests(TestCase):
    def test_signature_is_checked(self):
        self.assertEqual(telegram.verify_init_data(signed_init_data(42))["id"], 42)
        self.assertIsNone(telegram.verify_init_data(signed_init_data(42, token="other:token")))
        self.assertIsNone(telegram.verify_init_data(signed_init_data(42, auth_date=int(time.time()) - 3 * 86400)))
        tampered = signed_init_data(42).replace("Ali", "Bob")
        self.assertIsNone(telegram.verify_init_data(tampered))

    def test_linked_user_is_logged_in(self):
        user = make_user(telegram_chat_id="42")
        resp = self.client.post(reverse("telegram_mini_app_auth"), {"init_data": signed_init_data(42)})
        self.assertTrue(resp.json()["linked"])
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_unlinked_user_is_not_logged_in(self):
        resp = self.client.post(reverse("telegram_mini_app_auth"), {"init_data": signed_init_data(99)})
        self.assertFalse(resp.json()["linked"])
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_forged_data_is_rejected(self):
        make_user(telegram_chat_id="42")
        resp = self.client.post(reverse("telegram_mini_app_auth"), {"init_data": signed_init_data(42, token="x:y")})
        self.assertEqual(resp.status_code, 403)


@override_settings(TELEGRAM_BOT_TOKEN=TOKEN, TELEGRAM_WEBHOOK_SECRET="")
class BotLinkTests(TestCase):
    def test_link_code_is_single_use(self):
        user = make_user()
        code = user.telegram_link_code
        with mock.patch.object(telegram, "send_message"):
            telegram.handle_update({"message": {"text": f"/start {code}", "chat": {"id": 777}}})
            user.refresh_from_db()
            self.assertEqual(user.telegram_chat_id, "777")
            self.assertNotEqual(user.telegram_link_code, code)

            telegram.handle_update({"message": {"text": f"/start {code}", "chat": {"id": 888}}})
        user.refresh_from_db()
        self.assertEqual(user.telegram_chat_id, "777")

    def test_webhook_needs_derived_secret(self):
        url = lambda s: reverse("telegram_webhook", args=[s])  # noqa: E731
        self.assertEqual(self.client.post(url("cakebar-telegram"), "{}", content_type="application/json").status_code, 403)
        self.assertEqual(self.client.post(url(telegram.webhook_secret()), "{}", content_type="application/json").status_code, 200)
