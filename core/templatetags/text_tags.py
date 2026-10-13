from django import template
from core.utils.text import get_initials, get_telefone

register = template.Library()


@register.filter(name='initials')
def initials(value):
    return get_initials(value or '')


@register.filter(name='telefone')
def telefone(value):
    return get_telefone(value or '')
