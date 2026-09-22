from django.urls import path

from . import views

urlpatterns = [
    path("products/<int:product_id>/review/", views.review_create, name="review_create"),
]
