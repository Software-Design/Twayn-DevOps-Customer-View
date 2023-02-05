import datetime
import os
from typing import Union

import pdfkit
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseRedirect, FileResponse, Http404
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.encoding import iri_to_uri

from .models import *
from .templatetags.dates import parse_date
from .tools.gitlabCache import (loadIssues, loadMilestones, loadProject,
                                loadWikiPage)
from .tools.templateHelper import template
from .tools.viewsHelper import getProject
from .tools.sendMail import sendingEmail


def index(request: WSGIRequest) -> Union[HttpResponseRedirect, HttpResponse]:
    """
    Handles the requests for /
    Provites the login mechanism to authenticate users
    """

    if request.user.is_authenticated:
        return redirect('/overview/')
        
    if request.POST.get('email'):
        # It is allowed to login with both: email or username
        requestingUser = User.objects.filter(email=request.POST['email']).first()
        username = getattr(requestingUser, 'username', request.POST['email'])
        user = authenticate(request, username=username, password=request.POST['password'])

        if user:
            login(request, user)

            redirectUrl = request.GET.get('next')
            if(url_has_allowed_host_and_scheme(redirectUrl, None)):
                return redirect(iri_to_uri(redirectUrl))
            return redirect('/overview/')
        
        return redirect('/?error=invalid')
    
    return HttpResponse(template('login').render({}, request))


def loggingout(request: WSGIRequest) -> HttpResponseRedirect:
    """
    Handles the requests for /logout
    Logging out the user and redirects him to the index page
    """

    logout(request)
    return redirect('/')


@login_required
@staff_member_required
def reportsOverview(request: WSGIRequest) -> HttpResponse:
    """
    Handles the requests for /overview
    Gets all projects to show on the page
    """

    if request.user.is_staff:
        projectAssignments = UserProjectAssignment.objects.filter(project__closed=False).order_by('project__name').all()
    else:
        projectAssignments = UserProjectAssignment.objects.filter(project__closed=False,user=request.user)

    activeProjects = []
    inactiveProjects = []
    for assignment in projectAssignments:
        glProject = loadProject(assignment.project, assignment.accessToken)
        if glProject not in inactiveProjects and glProject not in activeProjects:
            try:
                if glProject['localProject'].inactive:
                    inactiveProjects.append(glProject)
                else:
                    activeProjects.append(glProject)
            except:
                activeProjects.append(glProject)

    return HttpResponse(template('report/view').render({'inactiveProjects': inactiveProjects, 'activeProjects': activeProjects}, request))


@login_required
def projectList(request: WSGIRequest) -> HttpResponse:
    """
    Handles the requests for /overview
    Gets all projects to show on the page
    """

    if request.user.is_staff:
        projectAssignments = UserProjectAssignment.objects.filter(project__closed=False).order_by('project__name').all()
    else:
        projectAssignments = UserProjectAssignment.objects.filter(project__closed=False,user=request.user)

    activeProjects = []
    inactiveProjects = []
    for assignment in projectAssignments:
        glProject = loadProject(assignment.project, assignment.accessToken)
        if glProject not in inactiveProjects and glProject not in activeProjects:
            try:
                if glProject['localProject'].inactive:
                    inactiveProjects.append(glProject)
                else:
                    activeProjects.append(glProject)
            except:
                activeProjects.append(glProject)

    return HttpResponse(template('project/list').render({'inactiveProjects': inactiveProjects, 'activeProjects': activeProjects}, request))


def projectPublic(request: WSGIRequest, slug:str, id:int, hash:str) -> HttpResponse:
    """
    Generate an overview for a project that is accesible without having an account
    """

    assignment = UserProjectAssignment.objects.filter(project__closed=False, project__projectIdentifier=id, project__privateUrlHash=hash).exclude(project__publicOverviewPassword__isnull=True,project__publicOverviewPassword__in=["", " ", None]).first()
    glProject = loadProject(assignment.project, assignment.accessToken)

    if request.POST.get('password'):
        if request.POST['password'] == assignment.project.publicOverviewPassword:
            request.session['password'] = request.POST.get('password')
        else:
            return redirect(f'/project/{slug}/{id}/{hash}?error=invalid')

    if request.GET.get('error'):
        return HttpResponse(template('publicOverview').render(glProject, request))

    if not request.session.get('password') or request.session.get('password') != assignment.project.publicOverviewPassword:
            return redirect(f'/project/{slug}/{id}/{hash}?error=loginrequired')


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

    return HttpResponse(template('project/public').render(glProject | {'fileTypes': DownloadableFile, 'daysbetween': daysbetween}, request))


@login_required
def projectView(request, slug:str, id:int) -> HttpResponse:
    
    glProject = getProject(request, id)
    if isinstance(glProject, HttpResponse):
        return glProject

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

    return HttpResponse(template('project/view').render(glProject | {'daysbetween': daysbetween}, request))


@login_required
def issueList(request, slug, id):
    """
    Handles the requests for /project/<slug:slug>/<int:id>/issues/
    Shows a paginated list of issues in this project
    """

    glProject = getProject(request, id)
    if isinstance(glProject, HttpResponse):
        return glProject

    glProject['issues'] = loadIssues(glProject['localProject'], glProject['remoteProject'], page=request.GET.get('page', 1), status=request.GET.get('status',None), label=request.GET.get('label',None))

    return HttpResponse(template('issue/list').render(glProject, request))


@login_required
def issueCreate(request: WSGIRequest, slug: str, id: int) -> Union[HttpResponseRedirect, HttpResponse]:
    """
    Handles the requests for /project/<slug:slug>/<int:id>/issues/create
    Creates a new issue for the project specified with the id
    """
    
    glProject = getProject(request, id)
    if isinstance(glProject, HttpResponse):
        return glProject

    if request.POST.get('title'):
        body = {'title': request.POST['title'], 'description': request.POST['description']}
        if request.POST.get('label','') != '':
            body['labels'] = request.POST['label']
        if request.POST.get('label','') != '':
            body['milestone_id'] = request.POST['milestone']
        url = '/project/'+glProject['remoteProject'].path+'/'+str(glProject['remoteProject'].id)+'/issues/'
        try:
            issue = glProject['remoteProject'].issues.create(body)
            cache.delete('glp_'+glProject['localProject'].projectIdentifier+'issues_'+str(issue.iid))
            if  settings.SEND_MAIL:
                milestone = loadMilestones(glProject['localProject'], glProject['remoteProject'],request.POST['milestone'])
                subjecttext = 'Hello, there is a new ticket in {}'.format(glProject['localProject'].name)
                messagetext = f'Title : {request.POST["title"]}\nLabel : {request.POST["label"]}\nMilestone : {milestone.title}\nDescription : {request.POST["description"]}'
                # send mail if ticket is saved       
                sendingEmail([glProject['localProject'].firstEMailAddress],messagetext,subjecttext)
        except:
            return redirect(url+'?error=invalid')
        return redirect(url)

        

    return HttpResponse(template('issue/create').render(glProject, request))


@login_required
def issue(request: WSGIRequest, slug: str, id: int, issue: int) -> HttpResponse:
    """
    Handles the requests for /project/<slug:slug>/<int:id>/issues/<int:issue>
    Get the information needed to display a single issue specified with the id and the issue (issue id)
    """

    glProject = getProject(request, id)
    if isinstance(glProject, HttpResponse):
        return glProject

    if request.POST.get('comment'):
        try:
            glProject['remoteProject'].issues.get(id=issue).notes.create({'body': '**'+request.user.first_name+' '+request.user.last_name+':**\n '+request.POST['comment']})
            id = 'glp_'+glProject['localProject'].projectIdentifier+'_issues_'+str(issue)
            cache.delete(id)
        except:
            return redirect('/project/'+glProject['remoteProject'].path+'/'+str(glProject['remoteProject'].id)+'/issues/'+str(issue)+'?error=invalid')

    glProject['issue'] = loadIssues(
        glProject['localProject'], glProject['remoteProject'], iid=issue)

    return HttpResponse(template('issue/view').render(glProject, request))


@login_required
def milestones(request: WSGIRequest, slug: str, id: int) -> HttpResponse:
    """
    Handles the requests for /project/<slug:slug>/<int:id>/milestones
    Get the information needed to display the milestones of the project specified with the id
    """

    glProject = getProject(request, id)
    if isinstance(glProject, HttpResponse):
        return glProject

    if not glProject['localProject'].enableDocumentation:
        return redirect('/')

    return HttpResponse(template('milestone/list').render(glProject, request))


@login_required
def milestoneBoard(request: WSGIRequest, slug: str, id: int, mid:int) -> HttpResponse:
    """
    Handles the requests for /project/<slug:slug>/<int:id>/milestone/<int:mid>
    Get the information needed to display a board of issues in this milestone
    """
    glProject = getProject(request, id)
    if isinstance(glProject, HttpResponse):
        return glProject

    if not glProject['localProject'].enableMilestones:
        return redirect('/')

    milestone = loadMilestones(glProject['localProject'], glProject['remoteProject'], mid)
    milestoneIssues = loadIssues(glProject['localProject'], glProject['remoteProject'], milestone=mid)
    issues = {'open': [], 'assigned': [], 'closed': [], 'timeEstimated': 0, 'timeSpent': 0}
    for issue in milestoneIssues: 
        if issue.state == 'closed':
            issues['closed'].append(issue)
        elif len(issue.assignees) > 0:
            issues['assigned'].append(issue)
        else:
            issues['open'].append(issue)
        time = issue.time_stats()
        issues['timeEstimated'] += time['time_estimate']
        issues['timeSpent'] += time['total_time_spent']
    
    issues['totalTime'] = issues['timeEstimated'] + issues['timeSpent']

    return HttpResponse(template('milestone/board').render(glProject | {'issues': issues, 'milestone': milestone, 'total': len(issues['open'])+len(issues['assigned'])+len(issues['closed'])}, request))

@login_required
def fileList(request: WSGIRequest, slug: str, id: int) -> HttpResponse:
    """
    Handles the requests for /project/<slug:slug>/<int:id>/download
    Get the information needed to display the files of the project specified with the id
    """

    glProject = getProject(request, id)
    if isinstance(glProject, HttpResponse):
        return glProject

    if not glProject['localProject'].enableDocumentation:
        return redirect('/')

    return HttpResponse(template('file/list').render(glProject | {'fileTypes': DownloadableFile}, request))

def fileDownload(request: WSGIRequest, slug: str, id: int, file: str) -> HttpResponse:
    """
    Given a file name from the uploads folder, download the file
    """

    assignment = UserProjectAssignment.objects.filter(project__projectIdentifier=id,project__closed=False).exclude(project__publicOverviewPassword__isnull=True,project__publicOverviewPassword__in=["", " ", None]).first()
    glProject = loadProject(assignment.project, assignment.accessToken)

    # Only bxpass the regular permission system if the project is public and the user has already authenticated himself with the public board password
    if not request.session.get('password') or not assignment.project.publicOverviewPassword or request.session.get('password') != assignment.project.publicOverviewPassword:
        glProject = getProject(request, id)
        if isinstance(glProject, HttpResponse):
            return glProject

    if not os.path.exists(settings.MEDIA_ROOT+file) or not glProject:
        raise Http404

    return FileResponse(open(settings.MEDIA_ROOT+file, 'rb'), as_attachment=True)

@login_required
def wiki(request: WSGIRequest, slug: str, id: int) -> Union[HttpResponseRedirect, HttpResponse]:
    """
    Handles the requests for /project/<slug:slug>/<int:id>/documentation
    Get the information needed to display an overview of the documentation pages of the project specified with the id
    Redirect to / if the documentation is disabled for the project
    """

    glProject = getProject(request, id)
    if isinstance(glProject, HttpResponse):
        return glProject

    if not glProject['localProject'].enableDocumentation:
        return redirect('/')

    return HttpResponse(template('wiki/overview').render(glProject, request))


@login_required
def wikiPage(request: WSGIRequest, slug: str, id: int, page) -> Union[HttpResponseRedirect, HttpResponse]:
    """
    Handles the requests for /project/<slug:slug>/<int:id>/documentation/<path:page>
    Get the information needed to display a single documentation page of the project specified with the id
    Redirect to / if the documentation is disabled for the project
    """

    glProject = getProject(request, id)
    if isinstance(glProject, HttpResponse):
        return glProject

    if not glProject['localProject'].enableDocumentation:
        return redirect('/')

    glProject['page'] = loadWikiPage(
        glProject['localProject'], glProject['remoteProject'], page)

    return HttpResponse(template('wiki/page').render(glProject, request))


@login_required
def printWiki(request: WSGIRequest, slug: str, id: int) -> Union[HttpResponseRedirect, HttpResponse]:
    """
    Handles the requests for /project/<slug:slug>/<int:id>/documentation/print
    Renders a pdf of the documentation pages to enable downloading them
    Redirect to / if the documentation is disabled for the project
    """

    glProject = getProject(request, id)
    if isinstance(glProject, HttpResponse):
        return glProject

    projectIdentifier = glProject['localProject'].projectIdentifier
    if not glProject['localProject'].enableDocumentation:
        return redirect('/')

    pdfkit.from_string(template('print/wiki').render(glProject, request), '/tmp/'+projectIdentifier+'.pdf', {'encoding': 'UTF-8', '--footer-center': '[page] '+_(
        'of')+' [topage]', '--footer-left': settings.INTERFACE_NAME, '--footer-right': datetime.datetime.now().strftime('%d.%m.%Y')}, verbose=True)

    with open('/tmp/'+projectIdentifier+'.pdf', 'rb') as f:
        file_data = f.read()

    os.remove('/tmp/'+projectIdentifier+'.pdf')

    response = HttpResponse(file_data, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="documentation.pdf"'

    return response

@login_required
def printOverview(request: WSGIRequest, slug: str, id:  int, date: str):
    """
    Handles the requests for /project/<slug:slug>/<int:id>/print/<str:date>
    Renders a pdf of the project overview to enable downloading it
    """

    glProject = getProject(request, id)
    if isinstance(glProject, HttpResponse):
        return glProject

    projectIdentifier = glProject['localProject'].projectIdentifier
    pdfkit.from_string(template('print/overview').render(glProject|{'issues': glProject['remoteProject'].issues.list(updated_after=datetime.datetime.strptime(date,'%Y-%m-%d'))}, request), '/tmp/'+projectIdentifier+'.pdf', {'encoding': 'UTF-8', '--footer-center': '[page] '+_(
        'of')+' [topage]', '--footer-left': settings.INTERFACE_NAME, '--footer-right': datetime.datetime.now().strftime('%d.%m.%Y')}, verbose=True)

    with open('/tmp/'+projectIdentifier+'.pdf', 'rb') as f:
        file_data = f.read()

    os.remove('/tmp/'+projectIdentifier+'.pdf')

    response = HttpResponse(file_data, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="overview.pdf"'

    return response


#
# Caching helpers
#

@login_required
@staff_member_required
def clearCache(request: WSGIRequest) -> HttpResponseRedirect:
    """
    Handles the requests for /cache/clear
    Resets the whole cache and redirects to /
    """

    cache.clear()

    redirectUrl = request.GET.get('redirect')
    if(url_has_allowed_host_and_scheme(redirectUrl, None)):
        return redirect(iri_to_uri(redirectUrl))
    return redirect('/')


@login_required
@staff_member_required
def warmupCache(request: WSGIRequest) -> HttpResponseRedirect:
    """
    Handles the requests for /cache/warmup
    Loads every project (from gitlab) and redirects to /
    """

    for project in Project.objects.all().prefetch_related('userprojectassignment_set'):
        if len(project.userprojectassignment_set.all()) > 0:
            # .first() will break the prefetch
            loadProject(project, project.userprojectassignment_set.all()[
                        0].accessToken)

    
    redirectUrl = request.GET.get('redirect')
    if(url_has_allowed_host_and_scheme(redirectUrl, None)):
        return redirect(iri_to_uri(redirectUrl))
    return redirect('/')



