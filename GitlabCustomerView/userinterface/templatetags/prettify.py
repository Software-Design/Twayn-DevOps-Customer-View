from django.template import Library
from userinterface.models import Employee

from django.utils.translation import gettext as _
import re

register = Library()

@register.filter(expects_localtime=True)
def translateDescriptions(value):

    # todo find a goot aproach to translate note bodys
    changedDescription = _('changed the description')
    assignedTo = _('assigned to %s')

    for employee in Employee.objects.all():
        value = _(re.sub('<[^<]+?>', '', value).replace(employee.gitlabUsername,'%s')).replace('%s',employee.name)
        
    return _(value)