from django.template import Library
import datetime

register = Library()

@register.filter(expects_localtime=True)
def dayssince(value):
    return(value - datetime.datetime.now()).days * -1