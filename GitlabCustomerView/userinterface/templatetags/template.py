from django.template import Library
from ..tools.templateHelper import template as t

register = Library()

@register.filter(expects_localtime=True)
def template(value):
    return t(value)