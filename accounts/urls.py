from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import PhoneLoginForm

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("password-reset/", views.password_reset, name="password_reset"),
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html", authentication_form=PhoneLoginForm), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/", views.profile, name="profile"),
    path("addresses/add/", views.address_add, name="address_add"),
    path("addresses/<int:pk>/delete/", views.address_delete, name="address_delete"),
]
