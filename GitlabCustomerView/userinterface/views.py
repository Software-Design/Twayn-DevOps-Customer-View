import os
import re
from typing import Union

import gitlab
import pdfkit
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils import translation

from .models import Project, UserProjectAssignment
from .templatetags.dates import parse_date
from .tools.gitlabCache import loadIssues, loadProject, loadWikiPage
from .tools.templateHelper import template
from .tools.viewsHelper import getProject


def index(request: WSGIRequest) -> Union[HttpResponseRedirect, HttpResponse]:
    """
    Handles the requests for /
    Provites the login mechanism to authenticate users
    """

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


def logginout(request: WSGIRequest) -> HttpResponseRedirect:
    """
    Handles the requests for /logout
    Logging out the user and redirects him to the index page
    """

    logout(request)
    return redirect('/')


@login_required
def overview(request: WSGIRequest) -> HttpResponse:
    """
    Handles the requests for /overview
    Gets all projects to show on the page
    """

    projectAssignments = UserProjectAssignment.objects.filter(user=request.user)

    projects = []
    for assignment in projectAssignments:
        glProject = loadProject(assignment.project, assignment.accessToken)
        if glProject not in projects:
            projects.append(glProject)

    return HttpResponse(template('overview').render({'projects': projects}, request))


@login_required
def project(request: WSGIRequest, slug: str, id: int) -> HttpResponse:
    """
    Handles the requests for /project/<slug:slug>/<int:id>
    Get all information needed to display a single project specified with the id
    """

    glProject = getProject(request, id) | {'localProject': project}

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
def issueList(request: WSGIRequest, slug: str, id: int) -> HttpResponse:
    """
    Handle the requests for /project/<slug:slug>/<int:id>/issues
    Get the information needed to display the issues of the project specified with the id
    """

    glProject = getProject(request, id)
    assigment = UserProjectAssignment.objects.get(user=request.user, project__projectIdentifier=id)
    glProject['issues'] = loadIssues(glProject['localProject'], assigment.accessToken, page=request.GET.get('page',1))
    
    return HttpResponse(template('issueList').render(glProject, request))


@login_required
def issueCreate(request: WSGIRequest, slug: str, id: int) -> Union[HttpResponseRedirect, HttpResponse]:
    """
    Handles the requests for /project/<slug:slug>/<int:id>/issues/create
    Creates a new issue for the project specified with the id
    """

    glProject = getProject(request, id)

    if request.POST.get('title'):
        glProject['project'].issues.create({'title': request.POST['title'], 'description': request.POST['description'], 'labels': request.POST['label'],'milestone_id': request.POST['milestone']})
        return redirect('/project/'+glProject['project'].path+'/'+str(glProject['project'].id)+'/issues/')

    return HttpResponse(template('issueCreate').render(glProject, request))


@login_required
def issue(request: WSGIRequest, slug: str, id: int, issue: int) -> HttpResponse:
    """
    Handles the requests for /project/<slug:slug>/<int:id>/issues/<int:issue>
    Get the information needed to display a single issue specified with the id and the issue (issue id)
    """

    glProject = getProject(request, id)
    assigment = UserProjectAssignment.objects.get(user=request.user, project__projectIdentifier=id)
    glProject['issue'] = loadIssues(glProject['localProject'], assigment.accessToken, iid=issue)
    
    return HttpResponse(template('issue').render(glProject, request))


@login_required
def milestones(request: WSGIRequest, slug: str, id: int) -> HttpResponse:
    """
    Handles the requests for /project/<slug:slug>/<int:id>/milestones
    Get the information needed to display the milestones of the project specified with the id
    """

    glProject = getProject(request, id)
    if not glProject['localProject'].enableDocumentation:
        return redirect('/')

    return HttpResponse(template('milestones').render(glProject, request))


@login_required
def wiki(request: WSGIRequest, slug: str, id: int) -> Union[HttpResponseRedirect, HttpResponse]:
    """
    Handles the requests for /project/<slug:slug>/<int:id>/documentation
    Get the information needed to display an overview of the documentation pages of the project specified with the id
    Redirect to / if the documentation is disabled for the project
    """

    glProject = getProject(request, id)
    if not glProject['localProject'].enableDocumentation:
        return redirect('/')
    
    return HttpResponse(template('wiki').render(glProject, request))


@login_required
def wikipage(request: WSGIRequest, slug: str, id: int, page) -> Union[HttpResponseRedirect, HttpResponse]:
    """
    Handles the requests for /project/<slug:slug>/<int:id>/documentation/<path:page>
    Get the information needed to display a single documentation page of the project specified with the id
    Redirect to / if the documentation is disabled for the project
    """

    glProject = getProject(request, id)
    if not glProject['localProject'].enableDocumentation:
        return redirect('/')

    assigment = UserProjectAssignment.objects.get(user=request.user, project__projectIdentifier=id)
    glProject['page'] = loadWikiPage(glProject['localProject'], assigment.accessToken, page)
    
    return HttpResponse(template('wikipage').render(glProject, request))


@login_required
def printWiki(request, slug, id):
    """
    Handles the requests for /project/<slug:slug>/<int:id>/documentation/print
    Renders a pdf of the documentation pages to enable downloading them
    Redirect to / if the documentation is disabled for the project
    """

    glProject = getProject(request, id)
    projectIdentifier = glProject['localProject'].projectIdentifier
    if not glProject['localProject'].enableDocumentation:
        return redirect('/')

    pdfkit.from_string(template('print/wiki').render(glProject, request), projectIdentifier+'.pdf', {'encoding': "UTF-8"})
    
    with open(projectIdentifier+'.pdf', 'rb') as f:
        file_data = f.read()
    
    os.remove(projectIdentifier+'.pdf')
    
    response = HttpResponse(file_data, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="documentation.pdf"'

    return response

#
# Caching helpers
#
@login_required
def clearCache(request: WSGIRequest) -> HttpResponseRedirect:
    """
    Handles the requests for /cache/clear
    Resets the whole cache and redirects to /
    """

    cache.clear()
    return redirect(request.GET.get('redirect','/'))


@login_required
def warmupCache(request: WSGIRequest) -> HttpResponseRedirect:
    """
    Handles the requests for /cache/warmup
    Loads every project (from gitlab) and redirects to /
    """

    for project in Project.objects.all().prefetch_related('userprojectassignment_set'):
        # TODO: loading every project in the cache may cause long waiting times if there are many projects
        if len(project.userprojectassignment_set.all()) > 0:
            # .first() will break the prefetch
            loadProject(project, project.userprojectassignment_set.all()[0].accessToken)

    return redirect(request.GET.get('redirect','/'))
