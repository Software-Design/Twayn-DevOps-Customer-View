import gitlab
from django.conf import settings
from django.core.cache import cache
from .wikiParser import parseStructure

def loadProject(projectId:int,accessToken:str):
    id = 'glp_'+projectId
    project = cache.get(id)
    if not project:
        gl = gitlab.Gitlab(url=settings.GITLAB_URL,private_token=accessToken)
        glProject = gl.projects.get(projectId)
        project = {'project': glProject,'milestones': glProject.milestones.list(),'issues': glProject.issues.list(order_by='updated_at', sort='desc')[:5],'wikis': parseStructure(glProject.wikis.list())}
        cache.set(id,project,settings.CACHE_PROJECTS)

    return project


def loadWikiPage(projectId:int,accessToken:str,slug:str):
    id = 'glp_'+projectId+'_'+slug
    page = cache.get(id)
    if not page:
        gl = gitlab.Gitlab(url=settings.GITLAB_URL,private_token=accessToken)
        project = gl.projects.get(projectId)
        page = project.wikis.get(slug)
        cache.set(id,page,settings.CACHE_PROJECTS)

    return page