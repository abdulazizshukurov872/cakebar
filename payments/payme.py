"""Payme (paycom.uz) merchant integration.

Checkout-link generation follows Payme's documented URL scheme, and the
webhook implements the standard JSON-RPC 2.0 "Merchant API" methods
(CheckPerformTransaction / CreateTransaction / PerformTransaction /
CancelTransaction / CheckTransaction / GetStatement).

Nothing here talks to Payme unless CAKEBAR_PAYME_MERCHANT_ID and
CAKEBAR_PAYME_KEY are set in the environment — see settings.py.
"""
import base64
import hmac
import json
import time

from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from orders.models import Order

from .models import Payment

# JSON-RPC error codes, per Payme's Merchant API spec.
ERROR_INVALID_AMOUNT = -31001
ERROR_TRANSACTION_NOT_FOUND = -31003
ERROR_CANNOT_CANCEL = -31007
ERROR_COULD_NOT_PERFORM = -31008
ERROR_ORDER_NOT_FOUND = -31050
ERROR_AUTH_FAILED = -32504
ERROR_METHOD_NOT_FOUND = -32601

STATE_CREATED = 1
STATE_COMPLETED = 2
STATE_CANCELLED = -1
STATE_CANCELLED_AFTER_COMPLETE = -2

# Payme cancels a transaction that was created but not performed within 12h.
TRANSACTION_TIMEOUT_MS = 12 * 60 * 60 * 1000


def is_configured():
    return bool(settings.PAYME_MERCHANT_ID and settings.PAYME_KEY)


def build_checkout_url(order):
    amount_tiyin = int(order.total_amount) * 100
    params = f"m={settings.PAYME_MERCHANT_ID};ac.order_id={order.id};a={amount_tiyin}"
    encoded = base64.b64encode(params.encode()).decode()
    host = "checkout.test.paycom.uz" if settings.PAYME_TEST else "checkout.paycom.uz"
    return f"https://{host}/{encoded}"


def _rpc_error(request_id, code, message):
    return JsonResponse({
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    })


def _rpc_result(request_id, result):
    return JsonResponse({"jsonrpc": "2.0", "id": request_id, "result": result})


def _check_auth(request):
    auth = request.META.get("HTTP_AUTHORIZATION", "")
    if not auth.startswith("Basic "):
        return False
    try:
        decoded = base64.b64decode(auth[6:]).decode()
        login, _, key = decoded.partition(":")
    except Exception:
        return False
    return login == "Paycom" and hmac.compare_digest(key.encode(), settings.PAYME_KEY.encode())


@csrf_exempt
@require_POST
def webhook(request):
    if not is_configured():
        return JsonResponse({"error": "Payme is not configured"}, status=503)

    try:
        payload = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return _rpc_error(None, -32700, "Parse error")

    request_id = payload.get("id")
    method = payload.get("method")
    params = payload.get("params") or {}

    if not _check_auth(request):
        return _rpc_error(request_id, ERROR_AUTH_FAILED, "Authorization failed")

    handlers = {
        "CheckPerformTransaction": _check_perform_transaction,
        "CreateTransaction": _create_transaction,
        "PerformTransaction": _perform_transaction,
        "CancelTransaction": _cancel_transaction,
        "CheckTransaction": _check_transaction,
        "GetStatement": _get_statement,
    }
    handler = handlers.get(method)
    if not handler:
        return _rpc_error(request_id, ERROR_METHOD_NOT_FOUND, "Method not found")
    return handler(request_id, params)


def _get_order(params):
    order_id = (params.get("account") or {}).get("order_id")
    if not order_id:
        return None
    return Order.objects.filter(id=order_id).first()


def _check_perform_transaction(request_id, params):
    order = _get_order(params)
    if not order:
        return _rpc_error(request_id, ERROR_ORDER_NOT_FOUND, "Order not found")
    amount_tiyin = int(order.total_amount) * 100
    if int(params.get("amount", -1)) != amount_tiyin:
        return _rpc_error(request_id, ERROR_INVALID_AMOUNT, "Incorrect amount")
    if not _order_payable(order):
        return _rpc_error(request_id, ERROR_COULD_NOT_PERFORM, "Order is cancelled or already paid")
    return _rpc_result(request_id, {"allow": True})


def _order_payable(order):
    """Only fresh card orders can be paid, not cancelled or expired ones."""
    if order.status != "yangi" or order.payment_method != "karta":
        return False
    return not Payment.objects.filter(order=order, state="performed").exists()


def _create_transaction(request_id, params):
    order = _get_order(params)
    if not order:
        return _rpc_error(request_id, ERROR_ORDER_NOT_FOUND, "Order not found")
    amount_tiyin = int(order.total_amount) * 100
    if int(params.get("amount", -1)) != amount_tiyin:
        return _rpc_error(request_id, ERROR_INVALID_AMOUNT, "Incorrect amount")

    trans_id = params["id"]
    payment, _ = Payment.objects.get_or_create(
        order=order, defaults={"provider": "payme", "amount": order.total_amount},
    )
    if payment.provider_transaction_id and payment.provider_transaction_id != trans_id:
        return _rpc_error(request_id, ERROR_COULD_NOT_PERFORM, "Another transaction already exists")
    if payment.state == "cancelled" and payment.provider_transaction_id == trans_id:
        return _rpc_error(request_id, ERROR_COULD_NOT_PERFORM, "Transaction was cancelled")
    if payment.provider_transaction_id != trans_id and not _order_payable(order):
        return _rpc_error(request_id, ERROR_COULD_NOT_PERFORM, "Order is cancelled or already paid")

    if not payment.provider_transaction_id:
        payment.provider_transaction_id = trans_id
        payment.save(update_fields=["provider_transaction_id"])

    return _rpc_result(request_id, {
        "create_time": int(payment.created_at.timestamp() * 1000),
        "transaction": str(payment.pk),
        "state": STATE_COMPLETED if payment.state == "performed" else STATE_CREATED,
    })


def _perform_transaction(request_id, params):
    trans_id = params["id"]
    payment = Payment.objects.filter(provider_transaction_id=trans_id, provider="payme").select_related("order").first()
    if not payment:
        return _rpc_error(request_id, ERROR_TRANSACTION_NOT_FOUND, "Transaction not found")

    if payment.state == "cancelled":
        return _rpc_error(request_id, ERROR_COULD_NOT_PERFORM, "Transaction was cancelled")
    if payment.state == "created" and payment.order.status == "bekor":
        # The order expired or was cancelled while the customer was paying.
        _mark_cancelled(payment, "Order cancelled before payment was performed")
        return _rpc_error(request_id, ERROR_COULD_NOT_PERFORM, "Order is cancelled")
    if payment.state == "created" and _is_timed_out(payment):
        _mark_cancelled(payment, "Payme reason code 4 (timeout)")
        payment.order.cancel(refund_money=False, reason="to'lov vaqti tugadi")
        return _rpc_error(request_id, ERROR_COULD_NOT_PERFORM, "Transaction timed out")

    if payment.state == "created":
        payment.state = "performed"
        payment.performed_at = timezone.now()
        payment.save(update_fields=["state", "performed_at"])
        order = payment.order
        if order.status == "yangi":
            order.status = "tasdiqlangan"
            order.save()

    return _rpc_result(request_id, {
        "transaction": str(payment.pk),
        "perform_time": int(payment.performed_at.timestamp() * 1000),
        "state": STATE_COMPLETED,
    })


def _cancel_transaction(request_id, params):
    trans_id = params["id"]
    payment = Payment.objects.filter(provider_transaction_id=trans_id, provider="payme").select_related("order").first()
    if not payment:
        return _rpc_error(request_id, ERROR_TRANSACTION_NOT_FOUND, "Transaction not found")

    reason = params.get("reason")
    if payment.state != "cancelled":
        _mark_cancelled(payment, f"Payme reason code {reason}")
        order = payment.order
        if order.status in ("yangi", "tasdiqlangan"):
            # Payme returns the money to the card itself, so no wallet credit.
            order.cancel(refund_money=False, reason="to'lov bekor qilindi")

    state = STATE_CANCELLED_AFTER_COMPLETE if payment.performed_at else STATE_CANCELLED
    return _rpc_result(request_id, {
        "transaction": str(payment.pk),
        "cancel_time": int(payment.cancelled_at.timestamp() * 1000),
        "state": state,
    })


def _mark_cancelled(payment, reason):
    payment.state = "cancelled"
    payment.cancelled_at = timezone.now()
    payment.error_reason = reason
    payment.save(update_fields=["state", "cancelled_at", "error_reason"])


def _is_timed_out(payment):
    age_ms = (timezone.now() - payment.created_at).total_seconds() * 1000
    return age_ms > TRANSACTION_TIMEOUT_MS


def _check_transaction(request_id, params):
    trans_id = params["id"]
    payment = Payment.objects.filter(provider_transaction_id=trans_id, provider="payme").first()
    if not payment:
        return _rpc_error(request_id, ERROR_TRANSACTION_NOT_FOUND, "Transaction not found")

    state_map = {"created": STATE_CREATED, "performed": STATE_COMPLETED, "cancelled": STATE_CANCELLED}
    return _rpc_result(request_id, {
        "create_time": int(payment.created_at.timestamp() * 1000),
        "perform_time": int(payment.performed_at.timestamp() * 1000) if payment.performed_at else 0,
        "cancel_time": int(payment.cancelled_at.timestamp() * 1000) if payment.cancelled_at else 0,
        "transaction": str(payment.pk),
        "state": state_map.get(payment.state, STATE_CREATED),
        "reason": None,
    })


def _get_statement(request_id, params):
    from_ms = params.get("from", 0)
    to_ms = params.get("to", int(time.time() * 1000))
    qs = Payment.objects.filter(
        provider="payme",
        created_at__gte=timezone.datetime.fromtimestamp(from_ms / 1000, tz=timezone.get_current_timezone()),
        created_at__lte=timezone.datetime.fromtimestamp(to_ms / 1000, tz=timezone.get_current_timezone()),
    )
    transactions = [{
        "id": p.provider_transaction_id,
        "time": int(p.created_at.timestamp() * 1000),
        "amount": int(p.amount) * 100,
        "account": {"order_id": str(p.order_id)},
        "create_time": int(p.created_at.timestamp() * 1000),
        "perform_time": int(p.performed_at.timestamp() * 1000) if p.performed_at else 0,
        "cancel_time": int(p.cancelled_at.timestamp() * 1000) if p.cancelled_at else 0,
        "transaction": str(p.pk),
        "state": {"created": STATE_CREATED, "performed": STATE_COMPLETED, "cancelled": STATE_CANCELLED}.get(p.state, STATE_CREATED),
        "reason": None,
    } for p in qs]
    return _rpc_result(request_id, {"transactions": transactions})
