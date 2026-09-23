from django.urls import path

from . import telegram, views

urlpatterns = [
    path("notifications/", views.notification_list, name="notification_list"),
    path("notifications/<int:pk>/open/", views.notification_open, name="notification_open"),
    path("telegram/webhook/<str:secret>/", telegram.webhook, name="telegram_webhook"),
    path("tg/", views.mini_app, name="telegram_mini_app"),
    path("tg/auth/", views.mini_app_auth, name="telegram_mini_app_auth"),
]
