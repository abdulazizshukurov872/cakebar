"""Tiny cache-based rate limiter for login / sign-up / password reset.

Counts attempts per key (IP address and phone number) in a fixed window.
Uses Django's cache, so with several server processes configure a shared
cache (Redis/database) for the limits to be global.
"""
from django.conf import settings
from django.core.cache import cache


def client_ip(request):
    if settings.IS_HOSTED:
        # Behind the host's proxy REMOTE_ADDR is the proxy; the proxy appends
        # the real client address as the last X-Forwarded-For entry (earlier
        # entries are client-supplied and can't be trusted).
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if forwarded:
            return forwarded.split(",")[-1].strip()
    return request.META.get("REMOTE_ADDR", "")


def normalize_phone(phone):
    return "".join(ch for ch in (phone or "") if ch.isdigit())


def _keys(scope, request, phone=""):
    keys = [f"rl:{scope}:ip:{client_ip(request)}"]
    phone = normalize_phone(phone)
    if phone:
        keys.append(f"rl:{scope}:phone:{phone}")
    return keys


def is_limited(scope, request, phone="", limit=None):
    limit = limit or settings.LOGIN_RATE_LIMIT
    return any((cache.get(key) or 0) >= limit for key in _keys(scope, request, phone))


def hit(scope, request, phone=""):
    for key in _keys(scope, request, phone):
        cache.add(key, 0, timeout=settings.LOGIN_RATE_WINDOW_SECONDS)
        try:
            cache.incr(key)
        except ValueError:  # expired between add() and incr()
            cache.set(key, 1, timeout=settings.LOGIN_RATE_WINDOW_SECONDS)


def reset(scope, request, phone=""):
    cache.delete_many(_keys(scope, request, phone))


LIMITED_MESSAGE = "Juda ko'p urinish. Iltimos, {minutes} daqiqadan keyin qayta urinib ko'ring."


def limited_message():
    return LIMITED_MESSAGE.format(minutes=max(1, settings.LOGIN_RATE_WINDOW_SECONDS // 60))
