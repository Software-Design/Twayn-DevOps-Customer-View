from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import Customer, Project

import gitlab



def index(request):

    template = loader.get_template(settings.TEMPLATE+'/login.html')

    return HttpResponse(template.render({},request))

def overview(request):

    template = loader.get_template(settings.TEMPLATE+'/overview.html')

    customer = Customer.objects.first()

    projects = []

    for project in customer.project_set.all():
        gl = gitlab.Gitlab(url=settings.GITLAB_URL,private_token=project.gitlabAccessToken)
        glProject = gl.projects.get(project.gitlabProjectId)
        projects.append(
            {'project': glProject, 'milestones': glProject.milestones.list()})

    return HttpResponse(template.render({'projects': projects}, request))

def project(request, slug, id):

    template = loader.get_template(settings.TEMPLATE+'/project.html')

    project = Project.objects.get(gitlabProjectId=id)

    gl = gitlab.Gitlab(url=settings.GITLAB_URL,private_token=project.gitlabAccessToken)
    glProject = gl.projects.get(project.gitlabProjectId)
    
    return HttpResponse(template.render({'project': glProject, 'milestones': glProject.milestones.list(), 'issues': glProject.issues.list(), 'wikis': glProject.wikis.list()}, request))

def issues(request, slug, id):

    template = loader.get_template(settings.TEMPLATE+'/project.html')

    project = Project.objects.get(gitlabProjectId=id)

    gl = gitlab.Gitlab(url=settings.GITLAB_URL,private_token=project.gitlabAccessToken)
    glProject = gl.projects.get(project.gitlabProjectId)
    
    return HttpResponse(template.render({'project': glProject, 'milestones': glProject.milestones.list(), 'issues': glProject.issues.list(), 'wikis': glProject.wikis.list()}, request))

def milestones(request, slug, id):

    template = loader.get_template(settings.TEMPLATE+'/project.html')

    project = Project.objects.get(gitlabProjectId=id)

    gl = gitlab.Gitlab(url=settings.GITLAB_URL,private_token=project.gitlabAccessToken)
    glProject = gl.projects.get(project.gitlabProjectId)
    
    return HttpResponse(template.render({'project': glProject, 'milestones': glProject.milestones.list(), 'issues': glProject.issues.list(), 'wikis': glProject.wikis.list()}, request))

def wiki(request, slug, id):

    template = loader.get_template(settings.TEMPLATE+'/project.html')

    project = Project.objects.get(gitlabProjectId=id)

    gl = gitlab.Gitlab(url=settings.GITLAB_URL,private_token=project.gitlabAccessToken)
    glProject = gl.projects.get(project.gitlabProjectId)
    
    return HttpResponse(template.render({'project': glProject, 'milestones': glProject.milestones.list(), 'issues': glProject.issues.list(), 'wikis': glProject.wikis.list()}, request))

def wikipage(request, slug, id):

    template = loader.get_template(settings.TEMPLATE+'/project.html')

    project = Project.objects.get(gitlabProjectId=id)

    gl = gitlab.Gitlab(url=settings.GITLAB_URL,private_token=project.gitlabAccessToken)
    glProject = gl.projects.get(project.gitlabProjectId)
    
    return HttpResponse(template.render({'project': glProject, 'milestones': glProject.milestones.list(), 'issues': glProject.issues.list(), 'wikis': glProject.wikis.list()}, request))
