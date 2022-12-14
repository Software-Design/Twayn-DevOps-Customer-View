from typing import Union

import gitlab
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import gettext as _
from gitlab.v4.objects.wikis import ProjectWiki
from userinterface.models import Project

from .wikiParser import parseStructure


def loadProject(projectObject: Project, accessToken: str) -> dict:
    """
    Loads the project from gitlab and all its information and returns them

    @return:
        dict:
            Either { 'remoteProject': GitLabProjectObject, 'localProject': Project, 'allMilestones': list or False, 'mostRecentIssues': list[:5], 'wikiPages': list or False, 'projectLabels':  }
            or { 'localProject': { 'name': 'projectName' }, 'error': 'An error occured: SomeException' }
    """

    id = f'glp_{projectObject.projectIdentifier}'

    project = cache.get(id)
    if not project:
        try:
            gl = gitlab.Gitlab(url=settings.GITLAB_URL,private_token=accessToken)
            glProject = gl.projects.get(projectObject.projectIdentifier)
        except Exception as e:
            return {
                'localProject': {'name': projectObject.name },
                'error': _('An error occurred')+': '+str(e)
                }

        project = {
                'remoteProject': glProject,
                'localProject': projectObject,
                'allMilestones': loadMilestones(projectObject, glProject),
                'mostRecentIssues': loadIssues(projectObject, glProject, page=1)[:5],
                'wikiPages': parseStructure(loadWikiPage(projectObject, glProject)),
                'projectLabels': loadLabels(projectObject, glProject),
                'projectReleases': loadReleases(projectObject, glProject),
            }
        cache.set(id,project,settings.CACHE_PROJECTS)

    return project


def loadWikiPage(projectObject: Project, tokenOrInstance, slug: str=None) -> Union[ProjectWiki, list]:
    """
    Loads a project wiki page or all wiki pages object from gitlab using the project identifier and slug

    @params:
        tokenOrInstance:
            Is either a string (token) or a gitlab.v4.objects.projects.Project instance

    @return:
        Either a single wiki page if slug is set or all pages of the project in a list
    """
    if not projectObject.enableDocumentation:
        return False

    project = getInstance(projectObject, tokenOrInstance)
    if slug:
        id = 'glp_'+projectObject.projectIdentifier+'_'+slug
    else:
        id = 'glp_'+projectObject.projectIdentifier

    page = cache.get(id)
    if not page:
        if slug:
            if not projectObject.wikiPrefix or slug.startswith(projectObject.wikiPrefix):
                page = project.wikis.get(slug)
        else:
            page = project.wikis.list()
        cache.set(id,page,settings.CACHE_PROJECTS)

    return page


def getInstance(projectObject: Project, tokenOrInstance):
    """
    Get the gitlab project object instance (remoteProject)

    @params:
        tokenOrInstance:
            Is either a string (token) or a gitlab.v4.objects.projects.Project instance
    
    @return:
        gitlab.v4.objects.projects.Project
    """

    if type(tokenOrInstance) == str:
        gl = gitlab.Gitlab(url=settings.GITLAB_URL,private_token=tokenOrInstance)
        project = gl.projects.get(projectObject.projectIdentifier)
    else:
        project = tokenOrInstance

    return project


def loadLabels(projectObject: Project, tokenOrInstance) -> list:
    """
    Loads the labels from gitlab for the given project object

    @params:
        tokenOrInstance:
            Is either a string (token) or a gitlab.v4.objects.projects.Project instance

    @return:
        list:
            A list containing ProjectLabel objects
            [ gitlab.v4.objects.labels.ProjectLabel, ... ]
    """
    
    project = getInstance(projectObject, tokenOrInstance)
    id = f'glp_{projectObject.projectIdentifier}_labels'

    labels = cache.get(id)
    if not labels:
        labels = []
        glLabels = project.labels.list()
        for label in glLabels:
            if not projectObject.labelPrefix or label.name.startswith(projectObject.labelPrefix):
                labels.append(label)
            
        cache.set(id,labels,settings.CACHE_PROJECTS)

    return labels


def loadReleases(projectObject: Project, tokenOrInstance) -> list:
    """
    Loads the releases from gitlab for the given project object

    @params:
        tokenOrInstance:
            Is either a string (token) or a gitlab.v4.objects.projects.Project instance

    @return:
        list:
            A list containing ProjectRelease objects
            [ gitlab.v4.objects.labels.ProjectRelease, ... ]
    """
    
    project = getInstance(projectObject, tokenOrInstance)
    id = f'glp_{projectObject.projectIdentifier}_releases'

    labels = cache.get(id)
    if not labels:
        glReleases = project.releases.list()
            
        cache.set(id,glReleases,settings.CACHE_PROJECTS)

    return glReleases

def loadMilestones(projectObject: Project, tokenOrInstance, iid:int=None) -> Union[list,dict]:
    """
    Loads the milestones from gitlab for the given project object

    @params:
        tokenOrInstance:
            Is either a string (token) or a gitlab.v4.objects.projects.Project instance
    
    @return:
        A list containing ProjectMilestone objects
        [ gitlab.v4.objects.milestones.ProjectMilestone, ... ]
    """
    
    if not projectObject.enableMilestones:
        return False

    project = getInstance(projectObject, tokenOrInstance)
    id = 'glp_'+projectObject.projectIdentifier+'_milestones'
    if iid:
        id = f'{id}_{str(iid)}'
    
    milestones = cache.get(id)
    if not milestones:
        if iid:
            milestones = project.milestones.get(iid)
        else:
            milestones = project.milestones.list()
        cache.set(id,milestones,settings.CACHE_MILESTONES)

    return milestones


def loadIssues(projectObject: Project, tokenOrInstance, iid: int=None, page: int=1, milestone:int=None, label:str=None, status:str=None) -> Union[list, dict, None]:
    """
    Loads an issue or the issues from gitlab for the given project object

    @params:
        tokenOrInstance:
            Is either a string (token) or a gitlab.v4.objects.projects.Project instance

    @return:
        Either a list containing ProjectIssue objects, an dict with the ProjectIssues or None
        [ gitlab.v4.objects.issues.ProjectIssue ... ] or { 'data': gitlab.v4.objects.issues.ProjectIssue, 'notes': [] } or None
    """

    project = getInstance(projectObject, tokenOrInstance)

    id = f'glp_{projectObject.projectIdentifier}_issues'
    if iid:
        id = f'{id}_{str(iid)}'
    elif milestone:
        id = f'{id}_m{str(milestone)}'
    elif label and status:
        id = f'{id}_ls{str(status)}_{str(label)}'
    elif label:
        id = f'{id}_l{str(label)}'
    elif status:
        id = f'{id}_s{str(status)}'
    id = f'{id}_p{str(page)}'

    issue = cache.get(id)
    if not issue:
        if iid:          
            issue = project.issues.get(iid)  
            if issue.confidential == True: 
                issue = None
            else:
                issue = {
                    'data': project.issues.get(iid),
                    'notes': issue.notes.list(system=False),
                    'mergeRequests': issue.related_merge_requests()
                }
        elif milestone:
            issue = project.milestones.get(milestone).issues(confidential=False, order_by='updated_at', sort='desc', page=page)
        elif label and status:
            issue = project.issues.list(confidential=False, order_by='updated_at', sort='desc', page=page, labels=label, state=status)
        elif label:
            issue = project.issues.list(confidential=False, order_by='updated_at', sort='desc', page=page, labels=label)
        elif status:
            print(status)
            issue = project.issues.list(confidential=False, order_by='updated_at', sort='desc', page=page, state=status)
        else:
            issue = project.issues.list(confidential=False, order_by='updated_at', sort='desc', page=page)
        cache.set(id,issue,settings.CACHE_ISSUES)

    return issue
