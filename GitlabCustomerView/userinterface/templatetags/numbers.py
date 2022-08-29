from django.template import Library
import re

register = Library()

@register.filter()
def intval (value):
    return int(re.findall(r'\d+', value)[0])