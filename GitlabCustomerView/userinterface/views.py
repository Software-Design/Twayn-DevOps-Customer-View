import re
from django.utils import translation
from django.http import HttpResponse
from django.core.cache import cache
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model

from .templatetags.dates import parse_date
from .models import UserProjectAssignment, Project
from .tools.gitlabCache import loadIssues, loadProject,loadWikiPage
from .tools.templateHelper import template

import gitlab

def index(request):

    if request.POST.get('email'):
        # dirty way to get the username of the user from the email
        UserModel = get_user_model()
        user = UserModel.objects.filter(email=request.POST.get('email')).first()
        user = authenticate(request, username=getattr(user, 'username', None), password=request.POST['password'])
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
    glProject = loadProject(project, assigment.accessToken) | {'localProject': project}

    firstMilestoneStart = None
    lastMilestoneEnd = None
    for milestone in glProject['allMilestones']:
        if milestone.start_date and milestone.due_date:
            start = parse_date(milestone.start_date)
            end = parse_date(milestone.due_date)
            if (milestone.expired == False or (milestone.expired == True and (end - start).days < 365)):
                if firstMilestoneStart == None or start < firstMilestoneStart:
                    firstMilestoneStart = start
                if lastMilestoneEnd == None or end > lastMilestoneEnd:
                    lastMilestoneEnd = end
    daysbetween = 0
    if lastMilestoneEnd and firstMilestoneStart:
        daysbetween = (lastMilestoneEnd - firstMilestoneStart).days
    
    return HttpResponse(template('project').render(glProject | {'daysbetween': daysbetween}, request))

@login_required
def issueList(request, slug, id):
    project = Project.objects.get(projectIdentifier=id)
    assigment = UserProjectAssignment.objects.get(user=request.user,project=project)
    glProject = loadProject(project, assigment.accessToken)
    glProject['issues'] = loadIssues(project, assigment.accessToken, page=request.GET.get('page',1))
    
    return HttpResponse(template('issueList').render(glProject, request))

@login_required
def issueCreate(request, slug, id):
    project = Project.objects.get(projectIdentifier=id)
    assigment = UserProjectAssignment.objects.get(user=request.user,project=project)

    glProject = loadProject(project, assigment.accessToken)

    if request.POST.get('title'):
        print(request.POST['label'])
        glProject['project'].issues.create({'title': request.POST['title'], 'description': request.POST['description'], 'labels': request.POST['label'],'milestone_id': request.POST['milestone']})
        return redirect('/project/'+glProject['project'].path+'/'+str(glProject['project'].id)+'/issues/')

    return HttpResponse(template('issueCreate').render(glProject, request))

@login_required
def issue(request, slug, id, issue):
    project = Project.objects.get(projectIdentifier=id)
    assigment = UserProjectAssignment.objects.get(user=request.user,project=project)
    glProject = loadProject(project, assigment.accessToken)
    glProject['issue'] = loadIssues(project, assigment.accessToken, iid=issue)
    
    return HttpResponse(template('issue').render(glProject, request))

@login_required
def milestones(request, slug, id):
    project = Project.objects.get(projectIdentifier=id)

    if project.enableMilestones == False:
        return redirect('/')

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
    glProject['page'] = loadWikiPage(project, assigment.accessToken, page)
    
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