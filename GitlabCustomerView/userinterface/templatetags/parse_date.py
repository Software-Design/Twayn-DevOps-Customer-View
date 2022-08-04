from django.template import Library
import datetime

register = Library()

@register.filter(expects_localtime=True)
def parse_iso(value):
    if(type(value) != str):
        return '?'
    return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")

@register.filter(expects_localtime=True)
def parse_date(value):
    if(type(value) != str):
        return '?'
    return datetime.datetime.strptime(value, "%Y-%m-%d")