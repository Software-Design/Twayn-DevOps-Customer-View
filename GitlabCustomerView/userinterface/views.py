from django.utils import translation
from django.http import HttpResponse
from django.core.cache import cache
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from .models import UserProjectAssignment, Project
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

    if request.user.is_authenticated:
        return redirect('/overview/')


    return HttpResponse(template('login').render({},request))

def logginout(request):
    logout(request)
    return redirect('/')

@login_required
def overview(request):
    projectAssignments = UserProjectAssignment.objects.filter(user=request.user)

    projects = []
    for assignment in projectAssignments:
        glProject = loadProject(assignment.project, assignment.accessToken)
        projects.append(glProject)

    return HttpResponse(template('overview').render({'projects': projects}, request))

@login_required
def project(request, slug, id):
    project = Project.objects.get(projectIdentifier=id)
    assigment = UserProjectAssignment.objects.get(user=request.user,project=project)
    glProject = loadProject(project, assigment.accessToken) | {'p': project}
    
    return HttpResponse(template('project').render(glProject, request))

@login_required
def issues(request, slug, id):
    project = Project.objects.get(projectIdentifier=id)
    assigment = UserProjectAssignment.objects.get(user=request.user,project=project)
    glProject = loadProject(project, assigment.accessToken)
    glProject['issues'] = loadIssues(project.projectIdentifier, assigment.accessToken, None, request.GET.get('page',1))
    
    return HttpResponse(template('issues').render(glProject, request))

@login_required
def issue(request, slug, id, issue):
    project = Project.objects.get(projectIdentifier=id)
    assigment = UserProjectAssignment.objects.get(user=request.user,project=project)
    glProject = loadProject(project, assigment.accessToken)
    glProject['issue'] = loadIssues(project.projectIdentifier, assigment.accessToken, issue, None)
    glProject['notes'] = glProject['issue'].notes.list(system=False)
    
    return HttpResponse(template('issue').render(glProject, request))

@login_required
def milestones(request, slug, id):
    project = Project.objects.get(projectIdentifier=id)
    assigment = UserProjectAssignment.objects.get(user=request.user,project=project)
    glProject = loadProject(project, assigment.accessToken)
    
    return HttpResponse(template('milestones').render(glProject, request))

@login_required
def wiki(request, slug, id):
    project = Project.objects.get(projectIdentifier=id)
    if project.enableDocumentation == False:
        return redirect('/')
    assigment = UserProjectAssignment.objects.get(user=request.user,project=project)
    glProject = loadProject(project, assigment.accessToken)
    
    return HttpResponse(template('wiki').render(glProject, request))

@login_required
def wikipage(request, slug, id, page):
    project = Project.objects.get(projectIdentifier=id)
    if project.enableDocumentation == False:
        return redirect('/')
    assigment = UserProjectAssignment.objects.get(user=request.user,project=project)
    glProject = loadProject(project, assigment.accessToken)
    glProject['page'] = loadWikiPage(project.projectIdentifier, assigment.accessToken, page)
    
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
    assigment = UserProjectAssignment.objects.all()
    for project in Project.objects.all():
        loadProject(project, project.assigment)
    return redirect(request.GET.get('redirect','/'))