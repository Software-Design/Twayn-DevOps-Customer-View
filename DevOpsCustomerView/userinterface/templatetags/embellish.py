from django.template import Library
from userinterface.models import TeamMember
from .dates import parse_date

from django.utils.translation import gettext as _
from datetime import datetime
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

@register.filter()
def firstMilestone(milestones):
    if len(milestones) > 0:
        return milestones[-1]
    return None

@register.filter()
def lastMilestone(milestones):
    milestones = sorted(milestones, key=lambda m: parse_date(m.due_date) if parse_date(m.due_date) != '?' else datetime(2020,1,1,0,0))
    if len(milestones) > 0:
        return milestones[-1]
    return None