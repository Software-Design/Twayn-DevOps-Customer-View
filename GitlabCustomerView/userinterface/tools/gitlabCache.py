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
            return {'project': {'name': projectObject.name },'error': _('An error occurred')+': '+str(e)}

        project = {'project': glProject,'milestones': glProject.milestones.list() if projectObject.enableMilestones else False,'issues': glProject.issues.list(confidential=False, order_by='updated_at', sort='desc')[:5],'wikis': parseStructure(glProject.wikis.list()) if projectObject.enableDocumentation else False}
        cache.set(id,project,settings.CACHE_PROJECTS)

    return project

def loadLabels(projectId:int,accessToken:str):
    id = 'glp_'+projectId+'_labels'
    labels = cache.get(id)
    if not labels:
        gl = gitlab.Gitlab(url=settings.GITLAB_URL,private_token=accessToken)
        labels = gl.projects.get(projectId).labels.list()
        cache.set(id,labels,settings.CACHE_PROJECTS)
    return labels

def loadWikiPage(projectId:int,accessToken:str,slug:str):
    id = 'glp_'+projectId+'_'+slug
    page = cache.get(id)
    if not page:
        gl = gitlab.Gitlab(url=settings.GITLAB_URL,private_token=accessToken)
        project = gl.projects.get(projectId)
        page = project.wikis.get(slug)
        cache.set(id,page,settings.CACHE_PROJECTS)

    return page

def loadIssues(projectId:int,accessToken:str,iid:int,page:int):
    gl = gitlab.Gitlab(url=settings.GITLAB_URL,private_token=accessToken)

    if iid:
        id = 'glp_'+projectId+'_issues_'+str(iid)
    else:
        id = 'glp_'+projectId+'_issues'
    
    issue = cache.get(iid)
    if not issue:
        project = gl.projects.get(projectId)
        if iid:
            issue = project.issues.get(iid)
            if issue.confidential == True: 
                issue = None
        else:
            issue = project.issues.list(confidential=False,page=page)  
        cache.set(id,issue,settings.CACHE_PROJECTS)

    return issue