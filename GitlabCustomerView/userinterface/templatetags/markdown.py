from django.template import Library
import markdown as md
import re

register = Library()

@register.filter()
def markdown(value):
    
    return re.sub("(^<p>|</p>$)", "",md.markdown(value))
