from os.path import exists
from django.template import loader
from django.conf import settings
from django.template.backends.django import Template

def template(name: str) -> Template:
    """
    Get the loaded template for the given name
    """

    path = settings.TEMPLATE+'/'+name+'.html'
    if exists(str(settings.BASE_DIR)+'/userinterface/templates/'+path):
        template = loader.get_template(path)
    else:
        template = loader.get_template('base/'+name+'.html')
    return template