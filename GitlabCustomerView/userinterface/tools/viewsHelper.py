# Purpose of this file:
# This file provides some helping functions primary for the views.py to prevent redundancy

from django.core.handlers.wsgi import WSGIRequest
from django.http import Http404
from userinterface.models import Project, UserProjectAssignment

from .gitlabCache import loadProject


def getProject(request: WSGIRequest, id: int) -> dict:
    """
    Get the project (currently only gitlab project) from the cache

    raises:
        Http404:
            If the requested project does not exist or is not linked to the requesting user
    """

    project = Project.objects.filter(projectIdentifier=id).first()

    if request.user.is_staff:
        assigment = UserProjectAssignment.objects.filter(project=project).first()
    else:
        assigment = UserProjectAssignment.objects.filter(user=request.user, project=project).first()

    if not project or not assigment:
        raise Http404

    # TODO: if we plan to support other things besides gitlab we should extend this to load even other projects (none-gitlab projects)
    return loadProject(project, assigment.accessToken)
