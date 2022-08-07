from django.conf import settings as django_settings
import datetime

def settings(request):
    return {
        'settings': django_settings,
        'now': datetime.datetime.today,
        'base': django_settings.TEMPLATE+'/base.html'
    }