"""Eskiz.uz SMS gateway client.

Only active once CAKEBAR settings ESKIZ_EMAIL/ESKIZ_PASSWORD are set. The
auth token is cached in-process for its ~30 day lifetime (Eskiz reissues a
long-lived JWT on login), so we log in once and reuse it.
"""
import logging

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

BASE_URL = "https://notify.eskiz.uz/api"
TOKEN_CACHE_KEY = "eskiz_auth_token"


def is_configured():
    return bool(settings.ESKIZ_EMAIL and settings.ESKIZ_PASSWORD)


def _login():
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        data={"email": settings.ESKIZ_EMAIL, "password": settings.ESKIZ_PASSWORD},
        timeout=8,
    )
    resp.raise_for_status()
    token = resp.json()["data"]["token"]
    cache.set(TOKEN_CACHE_KEY, token, timeout=60 * 60 * 24 * 25)
    return token


def _get_token():
    token = cache.get(TOKEN_CACHE_KEY)
    if token:
        return token
    return _login()


def send_sms(phone, message):
    if not is_configured():
        return False
    phone = "".join(ch for ch in phone if ch.isdigit())
    if phone.startswith("998") is False and len(phone) == 9:
        phone = "998" + phone

    token = _get_token()
    try:
        resp = requests.post(
            f"{BASE_URL}/message/sms/send",
            headers={"Authorization": f"Bearer {token}"},
            data={"mobile_phone": phone, "message": message, "from": "4546"},
            timeout=8,
        )
        if resp.status_code == 401:
            token = _login()
            resp = requests.post(
                f"{BASE_URL}/message/sms/send",
                headers={"Authorization": f"Bearer {token}"},
                data={"mobile_phone": phone, "message": message, "from": "4546"},
                timeout=8,
            )
        resp.raise_for_status()
        return True
    except requests.RequestException:
        logger.exception("Failed to send SMS via Eskiz to %s", phone)
        return False
