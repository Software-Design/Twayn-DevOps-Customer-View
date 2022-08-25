from django.utils import translation
from django.http import HttpResponse
from django.core.cache import cache
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login

from .models import Customer, Project
from .tools.gitlabCache import loadIssues, loadProject,loadWikiPage
from .tools.templateHelper import template

import gitlab

def index(request):

    if request.POST.get('username'):
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            return redirect('/overview/')
        else:
            return redirect('/')

    return HttpResponse(template('login').render({},request))

@login_required
def overview(request):
    customer = Customer.objects.first()

    projects = []
    for project in customer.project_set.all():
        glProject = loadProject(project.gitlabProjectId, project.gitlabAccessToken)
        projects.append(glProject)

    return HttpResponse(template('overview').render({'projects': projects}, request))

@login_required
def project(request, slug, id):
    project = Project.objects.get(gitlabProjectId=id)
    glProject = loadProject(project.gitlabProjectId, project.gitlabAccessToken)
    
    return HttpResponse(template('project').render(glProject, request))

@login_required
def issues(request, slug, id):
    project = Project.objects.get(gitlabProjectId=id)
    glProject = loadProject(project.gitlabProjectId, project.gitlabAccessToken)
    glProject['issues'] = loadIssues(project.gitlabProjectId, project.gitlabAccessToken,None,request.GET.get('page',1))
    
    return HttpResponse(template('issues').render(glProject, request))

@login_required
def issue(request, slug, id, issue):
    project = Project.objects.get(gitlabProjectId=id)
    glProject = loadProject(project.gitlabProjectId, project.gitlabAccessToken)
    glProject['issue'] = loadIssues(project.gitlabProjectId, project.gitlabAccessToken, issue, None)
    glProject['notes'] = glProject['issue'].notes.list(system=False)
    
    return HttpResponse(template('issue').render(glProject, request))

@login_required
def milestones(request, slug, id):
    project = Project.objects.get(gitlabProjectId=id)
    glProject = loadProject(project.gitlabProjectId, project.gitlabAccessToken)
    
    return HttpResponse(template('milestones').render(glProject, request))

@login_required
def wiki(request, slug, id):
    project = Project.objects.get(gitlabProjectId=id)
    glProject = loadProject(project.gitlabProjectId, project.gitlabAccessToken)
    
    return HttpResponse(template('wiki').render(glProject, request))

@login_required
def wikipage(request, slug, id, page):
    project = Project.objects.get(gitlabProjectId=id)
    glProject = loadProject(project.gitlabProjectId, project.gitlabAccessToken)
    glProject['page'] = loadWikiPage(project.gitlabProjectId, project.gitlabAccessToken, page)
    
    return HttpResponse(template('wikipage').render(glProject, request))

#
# Caching helpers
#
@login_required
def clearCache(request):
    cache.clear()
    return redirect(request.GET.get('redirect','/'))

@login_required
def warmupCache(request):
    for project in Project.objects.all():
        loadProject(project.gitlabProjectId, project.gitlabAccessToken)
    return redirect(request.GET.get('redirect','/'))