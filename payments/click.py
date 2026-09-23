"""Click (click.uz) merchant integration — Prepare/Complete handshake.

See https://docs.click.uz/en/click-api-request/ for the request/response
shapes this mirrors. Only active when CAKEBAR_CLICK_MERCHANT_ID,
CAKEBAR_CLICK_SERVICE_ID and CAKEBAR_CLICK_SECRET_KEY are all set.
"""
import hashlib
import hmac

from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from orders.models import Order

from .models import Payment

ERROR_SUCCESS = 0
ERROR_SIGN_FAILED = -1
ERROR_INCORRECT_AMOUNT = -2
ERROR_ACTION_NOT_FOUND = -3
ERROR_ALREADY_PAID = -4
ERROR_ORDER_NOT_FOUND = -5
ERROR_TRANSACTION_NOT_FOUND = -6
ERROR_TRANSACTION_CANCELLED = -9


def is_configured():
    return bool(settings.CLICK_MERCHANT_ID and settings.CLICK_SERVICE_ID and settings.CLICK_SECRET_KEY)


def build_checkout_url(order):
    return (
        "https://my.click.uz/services/pay"
        f"?service_id={settings.CLICK_SERVICE_ID}"
        f"&merchant_id={settings.CLICK_MERCHANT_ID}"
        f"&amount={int(order.total_amount)}"
        f"&transaction_param={order.id}"
    )


def _sign(fields):
    return hashlib.md5("".join(str(f) for f in fields).encode()).hexdigest()


def _error(error_code, error_note, **extra):
    return JsonResponse({"error": error_code, "error_note": error_note, **extra})


@csrf_exempt
@require_POST
def webhook(request):
    if not is_configured():
        return JsonResponse({"error": ERROR_ACTION_NOT_FOUND, "error_note": "Click is not configured"}, status=503)

    p = request.POST
    click_trans_id = p.get("click_trans_id", "")
    service_id = p.get("service_id", "")
    merchant_trans_id = p.get("merchant_trans_id", "")
    merchant_prepare_id = p.get("merchant_prepare_id", "")
    amount = p.get("amount", "0")
    action = p.get("action", "")
    sign_time = p.get("sign_time", "")
    sign_string = p.get("sign_string", "")

    if action == "0":
        expected = _sign([click_trans_id, service_id, settings.CLICK_SECRET_KEY, merchant_trans_id, amount, action, sign_time])
    else:
        expected = _sign([click_trans_id, service_id, settings.CLICK_SECRET_KEY, merchant_trans_id, merchant_prepare_id, amount, action, sign_time])

    if not hmac.compare_digest(sign_string.encode(), expected.encode()):
        return _error(ERROR_SIGN_FAILED, "SIGN CHECK FAILED", click_trans_id=click_trans_id, merchant_trans_id=merchant_trans_id)

    order = Order.objects.filter(id=merchant_trans_id).first()
    if not order:
        return _error(ERROR_ORDER_NOT_FOUND, "Order not found", click_trans_id=click_trans_id, merchant_trans_id=merchant_trans_id)

    if int(float(amount)) != int(order.total_amount):
        return _error(ERROR_INCORRECT_AMOUNT, "Incorrect amount", click_trans_id=click_trans_id, merchant_trans_id=merchant_trans_id)

    payment, _ = Payment.objects.get_or_create(order=order, defaults={"provider": "click", "amount": order.total_amount})

    if action == "0":
        if payment.state == "performed":
            return _error(ERROR_ALREADY_PAID, "Already paid", click_trans_id=click_trans_id, merchant_trans_id=merchant_trans_id)
        if order.status != "yangi" or payment.state == "cancelled":
            return _error(ERROR_TRANSACTION_CANCELLED, "Order is cancelled", click_trans_id=click_trans_id, merchant_trans_id=merchant_trans_id)
        payment.provider_transaction_id = click_trans_id
        payment.save(update_fields=["provider_transaction_id"])
        return _error(
            ERROR_SUCCESS, "Success",
            click_trans_id=click_trans_id, merchant_trans_id=merchant_trans_id,
            merchant_prepare_id=payment.pk,
        )

    if action == "1":
        if payment.state == "cancelled":
            return _error(ERROR_TRANSACTION_CANCELLED, "Transaction cancelled", click_trans_id=click_trans_id, merchant_trans_id=merchant_trans_id)
        if str(payment.pk) != str(merchant_prepare_id):
            return _error(ERROR_TRANSACTION_NOT_FOUND, "Transaction not found", click_trans_id=click_trans_id, merchant_trans_id=merchant_trans_id)

        error_code = p.get("error", "0")
        if error_code and int(error_code) < 0:
            payment.state = "cancelled"
            payment.cancelled_at = timezone.now()
            payment.error_reason = p.get("error_note", "")
            payment.save(update_fields=["state", "cancelled_at", "error_reason"])
            if order.status in ("yangi", "tasdiqlangan"):
                order.cancel(refund_money=False, reason="to'lov amalga oshmadi")
            return _error(ERROR_SUCCESS, "Success", click_trans_id=click_trans_id, merchant_trans_id=merchant_trans_id, merchant_confirm_id=payment.pk)

        if payment.state != "performed" and order.status == "bekor":
            return _error(ERROR_TRANSACTION_CANCELLED, "Order is cancelled", click_trans_id=click_trans_id, merchant_trans_id=merchant_trans_id)
        if payment.state != "performed":
            payment.state = "performed"
            payment.performed_at = timezone.now()
            payment.save(update_fields=["state", "performed_at"])
            if order.status == "yangi":
                order.status = "tasdiqlangan"
                order.save()

        return _error(ERROR_SUCCESS, "Success", click_trans_id=click_trans_id, merchant_trans_id=merchant_trans_id, merchant_confirm_id=payment.pk)

    return _error(ERROR_ACTION_NOT_FOUND, "Action not found", click_trans_id=click_trans_id, merchant_trans_id=merchant_trans_id)
