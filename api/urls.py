from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("categories", views.CategoryViewSet, basename="api-category")
router.register("products", views.ProductViewSet, basename="api-product")
router.register("orders", views.OrderViewSet, basename="api-order")

urlpatterns = [
    path("token/", obtain_auth_token, name="api_token_auth"),
] + router.urls
