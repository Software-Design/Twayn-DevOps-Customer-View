from django.template import Library
from django.utils.translation import gettext as _

# from ..tools.gitlabCache import loadWikiPage
from ..tools.viewsHelper import getRepositoryService

from ..models import *
import markdown as md
import re

register = Library()


customTranslations = {
    "(^<p>|</p>$)": "<br>",
    "\n": "<br>",
    r"\[ \] -": '<input type="checkbox" disabled>',
    r"\[x\] -": '<input type="checkbox" checked disabled>',
    r"\[ \]": '<input type="checkbox" disabled>',
    r"\[x\]": '<input type="checkbox" checked disabled>',
    '<ul>': '<ul class="list-group">',
    '<br><li>': '<li>',
    '<li>': '<li class="list-group-item">',
}

@register.filter()
def markdown(text):
    if not text:
        return ""
        
    text = md.markdown(text,extensions=['fenced_code', 'nl2br'])
    for key,value in customTranslations.items():
        text = re.sub(key,value,text)

    for employee in TeamMember.objects.all():
        text = text.replace('@'+employee.username,'%s').replace('%s',employee.name)
        text = text.replace(employee.username,'%s').replace('%s',employee.name)

    return text

@register.simple_tag
def wikicontent(slug,localProject, remoteProject):

    repService = getRepositoryService(localProject)
    text = repService.loadWikiPage(localProject, remoteProject, slug).content
    return markdown(text)