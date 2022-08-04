from django.template import Library
import markdown as md

register = Library()

@register.filter()
def markdown(value):
    
    return md.markdown(value)
