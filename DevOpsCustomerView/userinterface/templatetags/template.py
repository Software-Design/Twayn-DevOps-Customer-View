from django.template import Library
from ..tools.templateHelper import template as t

register = Library()

@register.filter(expects_localtime=True)
def template(value):
    return t(value)

@register.filter
def in_category(files, category):
    print(files)
    print(category)
    return files.filter(category=category)