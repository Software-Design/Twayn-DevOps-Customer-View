from django.template import Library
from django.utils.translation import gettext as _

from ..tools.gitlabCache import loadWikiPage
from ..models import *
import markdown as md
import re

register = Library()

@register.filter()
def markdown(value):

    customTranslations = {
        "(^<p>|</p>$)": "",
        "\[ \] -": '<input type="checkbox" disabled>',
        "\[x\] -": '<input type="checkbox" checked disabled>',
        "\[ \]": '<input type="checkbox" disabled>',
        "\[x\]": '<input type="checkbox" checked disabled>',
        '<ul>': '<ul class="list-group">',
        '<li>': '<li class="list-group-item">'
    }

    text = md.markdown(value)
    for key,value in customTranslations.items():
        text = re.sub(key,value,text)

    for employee in TeamMember.objects.all():
        text = text.replace('@'+employee.username,'%s').replace('%s',employee.name)

    return text

@register.simple_tag
def wikicontent(slug,localProject, remoteProject):
    return markdown(loadWikiPage(localProject, remoteProject, slug).content)