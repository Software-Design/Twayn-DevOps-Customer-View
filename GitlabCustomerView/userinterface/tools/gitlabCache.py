import gitlab
from django.conf import settings
from django.core.cache import cache


from .wikiParser import parseStructure
from userinterface.models import Project
from gitlab.v4.objects.wikis import ProjectWiki

from django.utils.translation import gettext as _


def loadProject(projectObject: Project, accessToken: str) -> dict:
    """
    Loads the project from gitlab and all its information and returns them

    @return:
        dict:
            { 'project': GitLabProjectObject, 'instance': Project, 'milestones': list or False, 'issues': list[:5], 'wikis': list or False }
    """

    id = f'glp_{projectObject.projectIdentifier}'

    project = cache.get(id)
    if not project:
        try:
            gl = gitlab.Gitlab(url=settings.GITLAB_URL,private_token=accessToken)
            glProject = gl.projects.get(projectObject.projectIdentifier)
        except Exception as e:
            return {'project': {'name': projectObject.name },'error': _('An error occurred')+': '+str(e)}

        project = {
                'project': glProject,
                'instance': projectObject,
                'milestones': glProject.milestones.list() if projectObject.enableMilestones else False,
                'issues': glProject.issues.list(confidential=False, order_by='updated_at', sort='desc')[:5],
                'wikis': parseStructure(glProject.wikis.list()) if projectObject.enableDocumentation else False
            }
        cache.set(id,project,settings.CACHE_PROJECTS)

    return project


def loadLabels(projectIdentifier: int, accessToken: str) -> list:
    """
    Loads the labels from gitlab for the specified project using the project identifier

    @return:
        list:
            A list containing ProjectLabel object
            [ gitlab.v4.objects.labels.ProjectLabel, ... ]
    """

    id = f'glp_{projectIdentifier}_labels'
    labels = cache.get(id)
    if not labels:
        gl = gitlab.Gitlab(url=settings.GITLAB_URL, private_token=accessToken)
        labels = gl.projects.get(projectIdentifier).labels.list()
        cache.set(id,labels,settings.CACHE_PROJECTS)
    return labels


def loadWikiPage(projectIdentifier: int, accessToken: str, slug: str) -> ProjectWiki:
    """
    Loads the project wiki page object from gitlab using the project identifier and slug
    """
    
    id = f'glp_{projectIdentifier}_{slug}'
    page = cache.get(id)
    if not page:
        gl = gitlab.Gitlab(url=settings.GITLAB_URL, private_token=accessToken)
        project = gl.projects.get(projectIdentifier)
        page = project.wikis.get(slug)
        cache.set(id,page,settings.CACHE_PROJECTS)

    return page


def loadIssues(projectIdentifier: int, accessToken: str, iid: int, page: int) -> list:
    """
    Loads the issues objects from gitlab in a list using the the project identifier and slug

    @return:
        list:
            A list containing ProjectIssue objects
            [ gitlab.v4.objects.issues.ProjectIssue ]
    """

    gl = gitlab.Gitlab(url=settings.GITLAB_URL,private_token=accessToken)

    id = f'glp_{projectIdentifier}_issues'
    if iid:
        id = f'{id}_{str(iid)}'
    
    issue = cache.get(iid)
    if not issue:
        project = gl.projects.get(projectIdentifier)
        if iid:
            issue = project.issues.get(iid)
            if issue.confidential == True: 
                issue = None
        else:
            issue = project.issues.list(confidential=False,page=page)  
        cache.set(id,issue,settings.CACHE_PROJECTS)

    return issue