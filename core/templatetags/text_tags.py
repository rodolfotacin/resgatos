from django import template
from core.utils.text import get_initials

register = template.Library()


@register.filter(name='initials')
def initials(value):
    return get_initials(value or '')