from django.template import Library
from userinterface.models import TeamMember

from django.utils.translation import gettext as _
import re

register = Library()

@register.filter()
def getTeamMember(value):
    member = TeamMember.objects.filter(username=value).first()
    if not member:
        member = TeamMember.objects.filter(username='@'+value).first()
    if not member:
        if re.match('@?project_(.*)_bot', value) != None:
            member = {'name': _('Customer')}
    return member

@register.filter('startswith')
def startswith(text, starts):
    return text.startswith(starts)

@register.filter('split')
def split(text, limit):
    return text.split(limit)