from django.conf import settings
from django.http import HttpResponse
from django.core.cache import cache

from .models import Customer, Project
from .tools.gitlabCache import loadIssues, loadProject,loadWikiPage
from .tools.templateHelper import template

import gitlab



def index(request):
    cache.clear()
    return HttpResponse(template('login').render({},request))

def overview(request):
    customer = Customer.objects.first()

    projects = []
    for project in customer.project_set.all():
        glProject = loadProject(project.gitlabProjectId, project.gitlabAccessToken)
        projects.append(glProject)

    return HttpResponse(template('overview').render({'projects': projects}, request))

def project(request, slug, id):
    project = Project.objects.get(gitlabProjectId=id)
    glProject = loadProject(project.gitlabProjectId, project.gitlabAccessToken)
    
    return HttpResponse(template('project').render(glProject, request))


def issues(request, slug, id):
    project = Project.objects.get(gitlabProjectId=id)
    glProject = loadProject(project.gitlabProjectId, project.gitlabAccessToken)
    glProject['issues'] = loadIssues(project.gitlabProjectId, project.gitlabAccessToken,None)
    
    return HttpResponse(template('issues').render(glProject, request))


def issue(request, slug, id, issue):
    project = Project.objects.get(gitlabProjectId=id)
    glProject = loadProject(project.gitlabProjectId, project.gitlabAccessToken)
    glProject['issue'] = loadIssues(project.gitlabProjectId, project.gitlabAccessToken, issue)
    glProject['notes'] = glProject['issue'].notes.list(system=False)
    
    return HttpResponse(template('issue').render(glProject, request))


def milestones(request, slug, id):
    project = Project.objects.get(gitlabProjectId=id)
    glProject = loadProject(project.gitlabProjectId, project.gitlabAccessToken)
    
    return HttpResponse(template('milestones').render(glProject, request))


def wiki(request, slug, id):
    project = Project.objects.get(gitlabProjectId=id)
    glProject = loadProject(project.gitlabProjectId, project.gitlabAccessToken)
    
    return HttpResponse(template('wiki').render(glProject, request))


def wikipage(request, slug, id, page):
    project = Project.objects.get(gitlabProjectId=id)
    glProject = loadProject(project.gitlabProjectId, project.gitlabAccessToken)
    glProject['page'] = loadWikiPage(project.gitlabProjectId, project.gitlabAccessToken, page)
    
    return HttpResponse(template('wikipage').render(glProject, request))

