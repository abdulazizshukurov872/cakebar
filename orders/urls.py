from django.urls import path

from . import views

urlpatterns = [
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/update/<str:key>/", views.cart_update, name="cart_update"),
    path("cart/remove/<str:key>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("my-orders/", views.order_list, name="order_list"),
    path("orders/<int:order_id>/cancel/", views.order_cancel, name="order_cancel"),
    path("orders/<int:order_id>/reorder/", views.order_reorder, name="order_reorder"),
    path("orders/<int:order_id>/status.json/", views.order_status_json, name="order_status_json"),
    path("orders/<int:order_id>/invoice.pdf/", views.order_invoice_pdf, name="order_invoice_pdf"),
    path("courier/", views.courier_panel, name="courier_panel"),
    path("courier/orders/<int:order_id>/status/", views.courier_update_status, name="courier_update_status"),
]
