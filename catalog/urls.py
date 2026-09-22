from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.product_list, name="product_list"),
    path("products/<int:product_id>/", views.product_detail, name="product_detail"),
    path("favorites/", views.favorite_list, name="favorite_list"),
    path("favorites/toggle/<int:product_id>/", views.favorite_toggle, name="favorite_toggle"),
]
