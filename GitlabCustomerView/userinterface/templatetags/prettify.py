from django.template import Library
from userinterface.models import TeamMember

from django.utils.translation import gettext as _
import re

register = Library()

@register.filter()
def translateDescriptions(value):

    # todo find a goot aproach to translate note bodys
    changedDescription = _('changed the description')
    assignedTo = _('assigned to %s')
    opened =_('opened')

    for employee in TeamMember.objects.all():
        value = _(re.sub('<[^<]+?>', '', value).replace(employee.username,'%s')).replace('%s',employee.name)
        
    return _(value)

@register.filter()
def getTeamMember(value):
    return TeamMember.objects.filter(username=value).first()

@register.filter('startswith')
def startswith(text, starts):
    return text.startswith(starts)

@register.filter('split')
def split(text, limit):
    return text.split(limit)