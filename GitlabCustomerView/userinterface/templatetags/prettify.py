from django.template import Library
from userinterface.models import Employee

register = Library()

@register.filter(expects_localtime=True)
def replaceUsernames(value):
    for employee in Employee.objects.all():
        value = value.replace(employee.gitlabUsername,employee.name)
    return value