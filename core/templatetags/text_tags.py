from django import template
from core.utils.text import get_initials, get_telefone, get_cpf

register = template.Library()


@register.filter(name='initials')
def initials(value):
    return get_initials(value or '')


@register.filter(name='telefone')
def telefone(value):
    return get_telefone(value or '')


@register.filter(name='cpf')
def cpf(value):
    return get_cpf(value or '')
