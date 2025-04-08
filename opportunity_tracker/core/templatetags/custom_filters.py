import re
from django import template
from django.utils.html import urlize, mark_safe
from django.utils.safestring import SafeString

register = template.Library()


@register.filter
def urlize_target_blank(value):
    value = urlize(value)

    value = re.sub(r'<a ', '<a target="_blank" ', value)

    return mark_safe(value)
