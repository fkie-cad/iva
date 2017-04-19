from django import template
from django.template.defaultfilters import stringfilter
from urllib.parse import unquote

register = template.Library()


@register.filter
@stringfilter
def decode_uri_binding(value):
    return unquote(value)


@register.filter
@stringfilter
def get_two_digits_number(number):
    return str(number).zfill(2)