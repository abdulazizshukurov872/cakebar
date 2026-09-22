from .translations import DEFAULT_LANG, LANGUAGES


def language(request):
    lang = request.session.get("lang", DEFAULT_LANG)
    return {"CUR_LANG": lang, "LANGUAGES": LANGUAGES}
