# Purpose of this file:
# This file provides some helping functions primary for the views.py to prevent redundancy

from typing import Union

from django.core.handlers.wsgi import WSGIRequest
from django.http import Http404, HttpResponse
from .templateHelper import template
from userinterface.models import Project, UserProjectAssignment

from .gitlabCache import gitlabServiceCache
from .githubCache import githubServiceCache


def getProject(request: WSGIRequest, id: int) -> Union[dict, HttpResponse]:
    """
    Get the project (currently only gitlab project) from the cache

    raises:
        Http404:
            If the requested project does not exist or is not linked to the requesting user
    """

    project = Project.objects.filter(projectIdentifier=id,closed=False).first()

    if not request.user.is_authenticated or not project:
        raise Http404

    if request.user.is_staff:
        assignment = UserProjectAssignment.objects.filter(project=project).first()
    else:
        assignment = UserProjectAssignment.objects.filter(user=request.user, project=project).first()

    if not project or not assignment:
        raise Http404

    # TODO: if we plan to support other things besides gitlab we should extend this to load even other projects (none-gitlab projects)
    repService = getRepositoryService(project)
    project = repService.loadProject(project, assignment.accessToken)
    if 'error' in project:
        if '404' in project['error']:
            raise Http404
        else:
            return HttpResponse(template('404').render({ **project }, request))

    return project

def getRepositoryService(projectObject: Project):
    if projectObject.repositoryService == Project.RepositoryServiceTypes.GITLAB:
        return gitlabServiceCache()
    elif projectObject.repositoryService == Project.RepositoryServiceTypes.GITHUB:
        return githubServiceCache()
