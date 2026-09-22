from django import template

from ..translations import get_text

register = template.Library()


def _current_lang(context):
    request = context.get("request")
    if request is not None:
        return request.session.get("lang", "uz")
    return "uz"


@register.simple_tag(takes_context=True)
def t(context, key):
    return get_text(_current_lang(context), key)


@register.simple_tag(takes_context=True)
def status_t(context, status_code):
    return get_text(_current_lang(context), f"status_{status_code}")


@register.simple_tag(takes_context=True)
def reason_t(context, reason_code):
    return get_text(_current_lang(context), f"reason_{reason_code}")


@register.simple_tag(takes_context=True)
def level_t(context, level_code):
    return get_text(_current_lang(context), f"level_{level_code}")


@register.simple_tag(takes_context=True)
def pfield(context, obj, field):
    return obj.localized(field, _current_lang(context))
