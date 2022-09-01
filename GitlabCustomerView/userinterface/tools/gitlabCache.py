import gitlab
from django.conf import settings
from django.core.cache import cache


from .wikiParser import parseStructure

from django.utils.translation import gettext as _

def loadProject(projectObject,accessToken:str):
    id = 'glp_'+projectObject.projectIdentifier

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
                'mostRecentIssues': loadIssues(projectObject, glProject, page=1),
                'wikiPages': parseStructure(loadWikiPage(projectObject, glProject)),
                'projectLabels': loadLabels(projectObject, glProject)
            }
        cache.set(id,project,settings.CACHE_PROJECTS)

    return project

def getInstance(projectObject, tokenOrInstance):

    if type(tokenOrInstance) == str:
        gl = gitlab.Gitlab(url=settings.GITLAB_URL,private_token=tokenOrInstance)
        project = gl.projects.get(projectObject.projectIdentifier)
    else:
        project = tokenOrInstance

    return project

def loadLabels(projectObject,tokenOrInstance):
    
    project = getInstance(projectObject, tokenOrInstance)
    id = 'glp_'+projectObject.projectIdentifier+'_labels'

    labels = cache.get(id)
    if not labels:
        labels = project.labels.list()
        cache.set(id,labels,settings.CACHE_PROJECTS)
    return labels

def loadMilestones(projectObject,tokenOrInstance):
    
    if not projectObject.enableMilestones:
        return False

    project = getInstance(projectObject, tokenOrInstance)
    id = 'glp_'+projectObject.projectIdentifier+'_milestones'

    milestones = cache.get(id)
    if not milestones:
        milestones = project.milestones.list()
        cache.set(id,milestones,settings.CACHE_PROJECTS)
    return milestones

def loadWikiPage(projectObject,tokenOrInstance,slug:str=None):

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

def loadIssues(projectObject,tokenOrInstance,iid:int=None,page:int=None):

    project = getInstance(projectObject, tokenOrInstance)

    if iid:
        id = 'glp_'+projectObject.projectIdentifier+'_issues_'+str(iid)
    else:
        id = 'glp_'+projectObject.projectIdentifier+'_issues_'+str(page)

    issue = cache.get(iid)
    if not issue:
        if iid:          
            issue = project.issues.get(iid)  
            if issue.confidential == True: 
                issue = None
            else:
                issue = {
                    'data': project.issues.get(iid),
                    'notes': issue.notes.list(system=False)
                }
        else:
            issue = project.issues.list(confidential=False, order_by='updated_at', sort='desc', page=page)
        cache.set(id,issue,settings.CACHE_PROJECTS)

    return issue