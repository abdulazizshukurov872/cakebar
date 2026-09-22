from django.urls import path

from . import views

urlpatterns = [
    path("orders/<int:order_id>/refund/", views.refund_create, name="refund_create"),
]
