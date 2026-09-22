from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/", views.role_redirect, name="dashboard"),
    path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"),
    path("dashboard/admin/export-orders/", views.export_orders_csv, name="export_orders_csv"),
    path("account/", views.account_home, name="account_home"),
]
