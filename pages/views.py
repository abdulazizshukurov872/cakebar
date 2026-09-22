from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .models import JobOpening, Location
from .translations import TRANSLATIONS


def set_lang(request, lang):
    if lang in TRANSLATIONS:
        request.session["lang"] = lang
    next_url = request.META.get("HTTP_REFERER", "")
    if not (next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()})):
        next_url = "/"
    return redirect(next_url)


def about(request):
    return render(request, "pages/about.html")


def locations(request):
    branches = Location.objects.all()
    return render(request, "pages/locations.html", {"branches": branches})


def restomarket(request):
    return render(request, "pages/restomarket.html")


def production(request):
    return render(request, "pages/production.html")


def events(request):
    return render(request, "pages/events.html")


def contacts(request):
    branches = Location.objects.all()
    return render(request, "pages/contacts.html", {"branches": branches})


def careers(request):
    jobs = JobOpening.objects.filter(is_active=True)
    return render(request, "pages/careers.html", {"jobs": jobs})
