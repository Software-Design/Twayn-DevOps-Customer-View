from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.core.cache import cache

from .models import Customer, Project
from .tools.gitlabCache import loadProject,loadWikiPage

import gitlab



def index(request):

    cache.clear()
    template = loader.get_template(settings.TEMPLATE+'/login.html')

    return HttpResponse(template.render({},request))

def overview(request):

    template = loader.get_template(settings.TEMPLATE+'/overview.html')

    customer = Customer.objects.first()

    projects = []

    for project in customer.project_set.all():
        gl = gitlab.Gitlab(url=settings.GITLAB_URL,private_token=project.gitlabAccessToken)
        glProject = loadProject(project.gitlabProjectId, project.gitlabAccessToken)
        projects.append(glProject)

    return HttpResponse(template.render({'projects': projects}, request))

def project(request, slug, id):

    template = loader.get_template(settings.TEMPLATE+'/project.html')

    project = Project.objects.get(gitlabProjectId=id)
    glProject = loadProject(project.gitlabProjectId, project.gitlabAccessToken)
    
    return HttpResponse(template.render(glProject, request))


def issues(request, slug, id):

    template = loader.get_template(settings.TEMPLATE+'/project.html')

    project = Project.objects.get(gitlabProjectId=id)
    glProject = loadProject(project.gitlabProjectId, project.gitlabAccessToken)
    
    return HttpResponse(template.render(glProject, request))


def milestones(request, slug, id):

    template = loader.get_template(settings.TEMPLATE+'/project.html')

    project = Project.objects.get(gitlabProjectId=id)
    glProject = loadProject(project.gitlabProjectId, project.gitlabAccessToken)
    
    return HttpResponse(template.render(glProject, request))


def wiki(request, slug, id):

    template = loader.get_template(settings.TEMPLATE+'/wiki.html')

    project = Project.objects.get(gitlabProjectId=id)
    glProject = loadProject(project.gitlabProjectId, project.gitlabAccessToken)
    
    return HttpResponse(template.render(glProject, request))


def wikipage(request, slug, id, page):

    template = loader.get_template(settings.TEMPLATE+'/wikipage.html')

    project = Project.objects.get(gitlabProjectId=id)
    glProject = loadProject(project.gitlabProjectId, project.gitlabAccessToken)
    glProject['page'] = loadWikiPage(project.gitlabProjectId, project.gitlabAccessToken, page)
    
    return HttpResponse(template.render(glProject, request))

