from django.urls import path

from . import views

urlpatterns = [
    path("chat/", views.customer_chat, name="customer_chat"),
    path("dashboard/chat/", views.admin_chat_list, name="admin_chat_list"),
    path("dashboard/chat/<int:user_id>/", views.admin_chat_detail, name="admin_chat_detail"),
]
