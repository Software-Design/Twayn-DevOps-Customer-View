from django.template import Library
from .prettify import replaceUsernames
import markdown as md
import re

register = Library()

@register.filter()
def markdown(value):

    customTranslations = {
        "(^<p>|</p>$)": "",
        "\[ \]": '<input type="checkbox" disabled>',
        "\[x\]": '<input type="checkbox" checked disabled>'
    }

    text = replaceUsernames(md.markdown(value))
    for key,value in customTranslations.items():
        text = re.sub(key,value,text)

    return text