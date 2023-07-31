from django.template import Library
import datetime

register = Library()

@register.filter(expects_localtime=True)
def parse_iso(value):
    if(type(value) != str or value == ''):
        return '?'
    return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")

@register.filter(expects_localtime=True)
def parse_date(value):
    # if already datetime object, return
    if(type(value) == datetime.datetime):
        return value
    if(type(value) != str or value == ''):
        return '?'
    return datetime.datetime.strptime(value, "%Y-%m-%d")

@register.filter(expects_localtime=True)
def dayssince(value):
    try:
        return(value - datetime.datetime.now()).days * -1
    except:
        return '?'