from django.urls import path

from . import click, payme

urlpatterns = [
    path("payments/payme/webhook/", payme.webhook, name="payme_webhook"),
    path("payments/click/webhook/", click.webhook, name="click_webhook"),
]
