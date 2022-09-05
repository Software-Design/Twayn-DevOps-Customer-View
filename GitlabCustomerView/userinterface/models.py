from django.db import models
from django.contrib.auth.models import User

class TeamMember(models.Model):
    """Overwrite profile information of GitLab Users

    More information on the descision to rewrite profile data
    https://gitlab.com/software-design-public/gitlab-customer-view/-/wikis/considerations/'TeamMember'-class
    """
    def __str__(self):
        return '{} ({})'.format(self.name, self.username)

    name = models.CharField(max_length=200)
    avatar = models.ImageField(blank=True)
    email = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    homepage = models.CharField(max_length=1000)
    username = models.CharField(max_length=200)

class Project(models.Model):
    """Representation of the hosted project

    This model should only contain a reference to the project and settings
    """
    def __str__(self):
        return '{} ({})'.format(self.name, self.projectIdentifier)

    assignees = models.ManyToManyField(TeamMember, blank=True)
    name = models.CharField(max_length=500)
    image = models.ImageField(blank=True)

    enableDocumentation = models.BooleanField(default=True,help_text="Make the documentation accessible for users")
    enableMilestones = models.BooleanField(default=True,help_text="Visualize milestones and create a gantt chart")
    enableTicketCreation = models.BooleanField(default=True,help_text="Allow customers to create new tickets")
    enableAddComments = models.BooleanField(default=True,help_text="Allow customers to create new comments")
    enableExports = models.BooleanField(default=True,help_text="Allow users to download contents of this project")

    showSystemNotes = models.BooleanField(default=True,help_text="Show system notes together wir comments")

    labelPrefix = models.CharField(max_length=500, help_text="User are not allowed to create issues with labels that don't start with this prefix", null=True, blank=True)
    wikiPrefix =  models.CharField(max_length=500, help_text="User are not allowed to view wiki pages with paths that don't start with this prefix", null=True, blank=True)
    # ... add more settings here

    projectIdentifier = models.CharField(max_length=200)

class UserProjectAssignment(models.Model):
    """Assignment between users and projects
    
    The assignment should also contain the authentication information (per user token)
    """
    def __str__(self):
        return '{} {} ({})'.format(self.user.first_name,self.user.last_name, self.project.name)

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    project = models.ForeignKey(Project,on_delete=models.CASCADE)

    accessToken = models.CharField(max_length=256)