from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("signup/verify/", views.signup_verify, name="signup_verify"),
    path("password-reset/", views.password_reset, name="password_reset"),
    path("login/", views.RateLimitedLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/", views.profile, name="profile"),
    path("addresses/add/", views.address_add, name="address_add"),
    path("addresses/<int:pk>/delete/", views.address_delete, name="address_delete"),
]
