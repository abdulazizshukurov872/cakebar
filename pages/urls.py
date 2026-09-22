from django.urls import path

from . import views

urlpatterns = [
    path("about/", views.about, name="about"),
    path("locations/", views.locations, name="locations"),
    path("restomarket/", views.restomarket, name="restomarket"),
    path("production/", views.production, name="production"),
    path("events/", views.events, name="events"),
    path("contacts/", views.contacts, name="contacts"),
    path("careers/", views.careers, name="careers"),
    path("set-lang/<str:lang>/", views.set_lang, name="set_lang"),
]
