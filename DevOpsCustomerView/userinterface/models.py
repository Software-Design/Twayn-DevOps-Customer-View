from django.db import models
from ckeditor.fields import RichTextField
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy
import os, hashlib, datetime

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
    homepage = models.CharField(max_length=1000,null=True,blank=True)
    username = models.CharField(max_length=200)

class Project(models.Model):
    """Representation of the hosted project

    This model should only contain a reference to the project and settings
    """
    def __str__(self):
        return '{} ({})'.format(self.name, self.projectIdentifier)

    def publicAccessHash(self):
        if not self.privateUrlHash:
            self.privateUrlHash = hashlib.md5((settings.SECRET_KEY+self.projectIdentifier+datetime.datetime.now().strftime(settings.DATETIME_FORMAT)).encode('utf-8')).hexdigest()
            self.save()
        return self.privateUrlHash

    assignees = models.ManyToManyField(TeamMember, blank=True)
    name = models.CharField(max_length=500)
    image = models.ImageField(blank=True)

    publicOverviewPassword = models.CharField(max_length=64,default="",null=True,blank=True,help_text="If no password is set, the public overview page is not accessible")
    publicOverviewText = RichTextField(null=True,blank=True)

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
    privateUrlHash = models.CharField(max_length=256, null=True)

    closed = models.BooleanField(default=False, help_text="If closed a project is no longer accessible or visible")

class UserProjectAssignment(models.Model):
    """Assignment between users and projects
    
    The assignment should also contain the authentication information (per user token)
    """
    def __str__(self):
        return '{} {} ({})'.format(self.user.first_name,self.user.last_name, self.project.name)

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    project = models.ForeignKey(Project,on_delete=models.CASCADE)

    accessToken = models.CharField(max_length=256)

class DownloadableFile(models.Model):
    """Files related to a project that can be downloaded by authenticated users with project access"""

    class DownloadableFileTypes(models.IntegerChoices):
            IMPORTANT = -1, gettext_lazy('Important Files & Links')
            CLIENT = 0, gettext_lazy('Customer data')
            OFFER = 10, gettext_lazy('Offers')
            DRAFT = 20, gettext_lazy('Draft')
            ORDER = 30, gettext_lazy('Orders')
            CONTRACT = 40, gettext_lazy('Contracts')
            PRIVACY = 50, gettext_lazy('Privacy documents')
            INVOICE = 60, gettext_lazy('Invoices')
            DEVELOPMENT = 64, gettext_lazy('Development')
            PRODUCTION = 65, gettext_lazy('Production')
            DOCUMENTATION = 70, gettext_lazy('Documentation')
            OTHER = 80, gettext_lazy('Other')

    def __str__(self):
        return '{} ({})'.format(self.name, self.project.name)

    name = models.CharField(max_length=200)
    order = models.IntegerField()
    category = models.IntegerField(max_length=200, choices=DownloadableFileTypes.choices)
    file = models.FileField(help_text="A downloadable file - must not be added if a link is set", null=True, blank=True)
    link = models.CharField(help_text="Link to a file or document - must not be set if a file is present", max_length=2000, null=True, blank=True)
    date = models.DateField()
    project = models.ForeignKey(Project,on_delete=models.CASCADE)

    def extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension[1:].upper()