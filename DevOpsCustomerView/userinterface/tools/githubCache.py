from typing import Union

import github
import re
from datetime import datetime, date, timezone
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import gettext as _
from gitlab.v4.objects.wikis import ProjectWiki
from userinterface.templatetags.dates import parse_date
from userinterface.models import Project
from .timetrackingHelper import calculateTime
from .wikiParser import parseStructure

from userinterface.tools.repositoryServiceInterface import RepositoryServiceInterface, remoteStdProject, remoteStdMilestone, remoteStdIssue, remoteStdUser, remoteStdMergeRequest, remoteStdNote

"""
    To get ID of repository from GitHub:
        HTML Source: <meta name="octolytics-dimension-repository_id" content="{ID}}">
"""
class githubServiceCache(RepositoryServiceInterface):
    def loadProject(self, projectObject: Project, accessToken: str) -> dict:
        """
        Loads the project from github and all its information and returns them

        @return:
            dict:
                Either { 'remoteProject': GitHubProjectObject, 'localProject': Project, 'allMilestones': list or False, 'mostRecentIssues': list[:5], 'wikiPages': list or False, 'projectLabels':  }
                or { 'localProject': { 'name': 'projectName' }, 'error': 'An error occured: SomeException' }
        """
        
        id = f'glh_{projectObject.projectIdentifier}'

        project = cache.get(id)
        if not project:
            try:
                # Only for self hosted github
                # gh = Github(base_url=settings.GITHUB_URL, login_or_token=accessToken)
                gh = github.Github(accessToken)
                # full_name_or_id, (str, int)
                ghProject = gh.get_repo(int(projectObject.projectIdentifier))
                ghProject.path = 'GitHub'
            except Exception as e:
                return {
                    'localProject': {'name': projectObject.name},
                    'error': _('An error occurred 123') + ': ' + str(e)
                }

            project = {
                'remoteProject': self.loadRemoteProject(projectObject, ghProject),
                'remoteInstance': ghProject,
                'localProject': projectObject,
                'allMilestones': self.loadMilestones(projectObject, ghProject),
                'mostRecentIssues': self.loadIssues(projectObject, ghProject)[:5],
                'wikiPages': [], #parseStructure(loadWikiPage(projectObject, ghProject)),
                'projectLabels': self.loadLabels(projectObject, ghProject),
                'projectReleases': self.loadReleases(projectObject, ghProject),
            }
            now = datetime.now()
            project['activeMilestones'] = [m for m in list(project['allMilestones']) if
                                          not m.expired and m.state == 'active' and
                                           m.start_date != '?' and m.start_date < now and
                                           m.due_date != '?' and m.due_date >= now]
            cache.set(id, project, settings.CACHE_PROJECTS)

        return project

    def loadRemoteProject(self, projectObject: Project, tokenOrInstance):
        project = self.getInstance(projectObject, tokenOrInstance)
        remoteProject = remoteStdProject()

        remoteProject.id = project.id
        remoteProject.remoteIdentifier = project.id
        remoteProject.path = "GitHub"
        remoteProject.avatar_url = ""
        remoteProject.description = project.description
        remoteProject.web_url = project.url

        return remoteProject

    def loadLabels(self, projectObject: Project, tokenOrInstance) -> list:
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

        project = self.getInstance(projectObject, tokenOrInstance)
        id = f'glh_{projectObject.projectIdentifier}_labels'

        labels = cache.get(id)
        if not labels:
            labels = []
            ghLabels = project.get_labels()
            for label in ghLabels:
                if not projectObject.labelPrefix or label.name.startswith(projectObject.labelPrefix):
                    labels.append(label)

            cache.set(id, labels, settings.CACHE_PROJECTS)

        return labels

    def loadReleases(self, projectObject: Project, tokenOrInstance) -> list:
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

        # ToDo: No releaases!!!
        return []

        project = self.getInstance(projectObject, tokenOrInstance)
        id = f'glh_{projectObject.projectIdentifier}_releases'

        ghReleases = []
        labels = cache.get(id)
        if not labels:
            ghReleases = project.releases.list()

            cache.set(id, ghReleases, settings.CACHE_PROJECTS)

        return ghReleases

    def loadMilestones(self, projectObject: Project, tokenOrInstance, iid: int = None) -> Union[list, dict]:
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
            return []

        project = self.getInstance(projectObject, tokenOrInstance)
        id = 'glh_' + projectObject.projectIdentifier + '_milestones'
        if iid:
            id = f'{id}_{str(iid)}'

        milestones = cache.get(id)
        if not milestones:
            milestones = []
            if iid:
                remoteMilestone = project.get_milestone(number=iid)
                newMilestone = self.convertMilestone(remoteMilestone)
                milestones = newMilestone
            else:
                remoteMilestones = project.get_milestones()
                # as there is no start date in github, use due date from last milestone
                remoteMilestones = sorted(remoteMilestones, key=lambda m: m.due_on if m.due_on != '?' and m.due_on else datetime(2020, 1, 1, 0, 0), reverse=False)
                lastStartDate = datetime(2020, 1, 1, 0, 0)
                for remoteMilestone in remoteMilestones:
                    newMilestone = self.convertMilestone(remoteMilestone, lastStartDate)
                    milestones.append(newMilestone)
                    lastStartDate = newMilestone.due_date
                milestones = sorted(milestones, key=lambda m: m.due_date if m.due_date != '?' and m.due_date else datetime(2020, 1, 1, 0, 0), reverse=True)

            cache.set(id, milestones, settings.CACHE_MILESTONES)

        return milestones

    def convertMilestone(self, remoteMilestone, startDate=datetime(2020, 1, 1, 0, 0)):
        newMilestone = remoteStdMilestone()
        newMilestone.id = remoteMilestone.id
        newMilestone.remoteIdentifier = remoteMilestone.number
        newMilestone.title = remoteMilestone.title
        newMilestone.description = remoteMilestone.description
        newMilestone.state = remoteMilestone.state
        newMilestone.isActive = newMilestone.state == 'open'
        newMilestone.expired = (datetime.now() - remoteMilestone.due_on).days > 0 if remoteMilestone.due_on else False
        newMilestone.start_date = startDate
        newMilestone.due_date = remoteMilestone.due_on
        newMilestone.web_url = remoteMilestone.url

        return newMilestone

    # def calcStartDateMilestones(self, beforeMilestones):
    #     afterMilestones = []
    #     for idx, milestone in enumerate(beforeMilestones):
    #         if idx > 0:
    #             milestone.start_date = beforeMilestones[idx - 1].due_on
    #         else:
    #             milestone.start_date = datetime(2020, 1, 1, 0, 0)
    #         afterMilestones.append(milestone)
    #
    #     return afterMilestones

    def loadIssues(self, projectObject: Project, tokenOrInstance, iid: int = None, page: int = 1, milestone: int = None,
                   label: str = None, status: str = None) -> Union[list, dict, None]:
        """
        Loads an issue or the issues from gitlab for the given project object

        @params:
            tokenOrInstance:
                Is either a string (token) or a gitlab.v4.objects.projects.Project instance

        @return:
            Either a list containing ProjectIssue objects, an dict with the ProjectIssues or None
            [ gitlab.v4.objects.issues.ProjectIssue ... ] or { 'data': gitlab.v4.objects.issues.ProjectIssue, 'notes': [] } or None
        """
        # make some transformations
        if status == 'opened':
            status = 'open'
        elif status == 'closed':
            status = 'closed'

        if type(label) == str:
            label = [label]


        project = self.getInstance(projectObject, tokenOrInstance)

        id = f'glh_{projectObject.projectIdentifier}_issues'
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

        issues = cache.get(id)
        if not issues:
            issues = []
            remoteIssues = []
            if iid:
                remoteIssue = project.get_issue(iid)
                newIssue = self.convertIssue(remoteIssue)

                # ToDo how to get pull request for issue???
                mergeRequests = []
                # for remoteMergeRequest in remoteIssue.get_pulls():
                #     newMR = self.convertMergeRequest(remoteMergeRequest)
                #     mergeRequests.append(newMR)

                notes = []
                for remoteNote in remoteIssue.get_comments():
                    newNote = self.convertNote(remoteNote)
                    newIssue = calculateTime(newIssue, newNote.body)
                    notes.append(newNote)

                newIssue.notes = notes
                # ToDo: There is no confidential in github, any alternative?
                issues = {
                    'data': newIssue,
                    'notes': notes,
                    'mergeRequests': mergeRequests
                }
            elif milestone:
                milestone = project.get_milestone(number=int(milestone))
                remoteIssues = project.get_issues(milestone=milestone, state='all', sort='updated', direction='desc')
            elif label and status:
                remoteIssues = project.get_issues(labels=label, state=status, sort='updated', direction='desc')
            elif label:
                remoteIssues = project.get_issues(labels=label, state='all', sort='updated', direction='desc')
            elif status:
                remoteIssues = project.get_issues(state=status, sort='updated', direction='desc')
            else:
                remoteIssues = project.get_issues(state='all', sort='updated', direction='desc')

            for remoteIssue in remoteIssues:
                newIssue = self.convertIssue(remoteIssue)
                notes = []

                for remoteNote in remoteIssue.get_comments():
                    newNote = self.convertNote(remoteNote)
                    newIssue = calculateTime(newIssue, newNote.body)
                    notes.append(newNote)

                newIssue.notes = notes
                issues.append(newIssue)

            cache.set(id, issues, settings.CACHE_ISSUES)

            cache.set(id, issues, settings.CACHE_ISSUES)

        return issues

    def convertIssue(self, remoteIssue):
        newIssue = remoteStdIssue()
        newIssue.id = remoteIssue.id
        newIssue.iid = remoteIssue.number
        newIssue.remoteIdentifier = remoteIssue.number
        newIssue.confidential = False
        newIssue.state = remoteIssue.state
        newIssue.isOpen = newIssue.state == 'open'
        newIssue.title = remoteIssue.title
        newIssue.description = remoteIssue.body
        newIssue.created_at = remoteIssue.created_at
        newIssue.updated_at = remoteIssue.updated_at
        newIssue.due_date = None
        newIssue.closed_at = remoteIssue.closed_at
        newIssue.web_url = remoteIssue.url
        newIssue.user_notes_count = remoteIssue.comments
        newIssue.author = self.convertUser(remoteIssue.user)

        if remoteIssue.assignees:
            newIssue.assignees = []
            for assignee in remoteIssue.assignees:
                newUser = self.convertUser(assignee)
                newIssue.assignees.append(newUser)

        if remoteIssue.milestone:
            newIssue.milestone = self.convertMilestone(remoteIssue.milestone)

        if remoteIssue.labels:
            newIssue.labels = []
            for label in remoteIssue.labels:
                newIssue.labels.append(label.name)

        # if remoteIssue.time_stats():
        #     newIssue.time_stats_human_time_estimate = 0
        #     newIssue.time_stats_human_total_time_spent = 0
        #     newIssue.time_stats_time_estimate = 0
        #     newIssue.time_stats_total_time_spent = 0

        return newIssue

    def convertUser(self, remoteUser):
        newUser = remoteStdUser()
        newUser.id = remoteUser.id
        newUser.state = ""
        newUser.username = remoteUser.login
        newUser.name = remoteUser.login
        newUser.web_url = remoteUser.html_url

        return newUser

    def convertMergeRequest(self, remoteMergeRequest):
        newMergeRequest = remoteStdMergeRequest()
        newMergeRequest.id = remoteMergeRequest.id
        newMergeRequest.iid = remoteMergeRequest.number
        newMergeRequest.remoteIdentifier = remoteMergeRequest.number
        newMergeRequest.title = remoteMergeRequest.title
        newMergeRequest.description = remoteMergeRequest.body
        newMergeRequest.state = remoteMergeRequest['state']
        newMergeRequest.created_at = remoteMergeRequest.created_at
        newMergeRequest.updated_at = remoteMergeRequest.updated_at
        newMergeRequest.user_notes_count = remoteMergeRequest.comments
        newMergeRequest.draft = remoteMergeRequest.draft
        # newMergeRequest.work_in_progress = True
        # ToDo check!
        newMergeRequest.changes_count = remoteMergeRequest.commits
        newMergeRequest.web_url = remoteMergeRequest.html_url

        return newMergeRequest

    def convertNote(self, remoteNote):
        newNote = remoteStdNote()
        newNote.id = remoteNote.id
        newNote.body = remoteNote.body
        newNote.created_at = remoteNote.created_at
        newNote.updated_at = remoteNote.updated_at
        newNote.confidential = False
        newNote.internal = False
        newNote.author = self.convertUser(remoteNote.user)

        return newNote


    def loadWikiPage(self, projectObject: Project, tokenOrInstance, slug: str = None) -> Union[ProjectWiki, list]:
        """
        Loads a project wiki page or all wiki pages object from gitlab using the project identifier and slug

        @params:
            tokenOrInstance:
                Is either a string (token) or a gitlab.v4.objects.projects.Project instance

        @return:
            Either a single wiki page if slug is set or all pages of the project in a list
        """

        # ToDo: No wikis!!!
        return False

        if not projectObject.enableDocumentation:
            return False

        project = self.getInstance(projectObject, tokenOrInstance)
        if slug:
            id = 'glh_' + projectObject.projectIdentifier + '_' + slug
        else:
            id = 'glh_' + projectObject.projectIdentifier

        page = cache.get(id)
        if not page:
            if slug:
                if not projectObject.wikiPrefix or slug.startswith(projectObject.wikiPrefix):
                    page = project.wikis.get(slug)
            else:
                page = project.wikis.list()
            cache.set(id, page, settings.CACHE_PROJECTS)

        return page

    def createIssue(self, projectObject: Project, tokenOrInstance, title: str, description='', milestoneIdentifier='',
                    labels=''):
        project = self.getInstance(projectObject, tokenOrInstance)

        newIssue = {"title": title, "body": description}

        if labels != '' and type(labels) == str:
            labels = [labels]
            newIssue['labels'] = labels

        if milestoneIdentifier != '':
            milestone = project.get_milestone(number=int(milestoneIdentifier))
            newIssue['milestone'] = milestone

        issue = project.create_issue(**newIssue)

        cache.delete('glh_' + projectObject.projectIdentifier + 'issues_' + str(issue.number))

        return True

    def createIssueComment(self, projectObject: Project, tokenOrInstance, issue: int, body: str):
        project = self.getInstance(projectObject, tokenOrInstance)

        issue = project.get_issue(issue).create_comment(body)

        id = 'glp_' + projectObject.projectIdentifier + '_issues_' + str(issue)
        cache.delete(id)

        return True

    def lastUpdate(self, projectObject: Project, tokenOrInstance):
        project = self.getInstance(projectObject, tokenOrInstance)
        lastUpdate = project.updated_at
        if (lastUpdate < project.pushed_at):
            lastUpdate = project.pushed_at

        remoteIssues = project.get_issues(state='all', sort='updated', direction='desc', since=lastUpdate)
        if (remoteIssues.totalCount > 0):
            lastUpdate = remoteIssues[0].updated_at

        import django
        return django.utils.timezone.make_aware(lastUpdate, timezone.utc)

    def getInstance(self, projectObject: Project, tokenOrInstance):
        """
        Get the github repository object instance (remoteProject)

        @params:
            tokenOrInstance:
                Is either a string (token) or a gitlab.v4.objects.projects.Project instance

        @return:
            github
        """

        if type(tokenOrInstance) == str:
            # Only for self hosted github
            # gh = Github(base_url=settings.GITHUB_URL, login_or_token=tokenOrInstance)
            # ToDo: not working or used ???
            ### gh = Github(login_or_token=tokenOrInstance)
            ### project = gh.projects.get(projectObject.projectIdentifier)
            # full_name_or_id, (str, int)
            gh = github.Github(tokenOrInstance)
            ghProject = gh.get_repo(int(projectObject.projectIdentifier))
            ghProject.path = 'GitHub'
            project = ghProject
        else:
            project = tokenOrInstance

        return project