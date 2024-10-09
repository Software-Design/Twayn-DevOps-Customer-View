import datetime
import hashlib
import os

from ckeditor.fields import RichTextField
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _


class Company(models.Model):
    """Model representing a customer company."""

    name = models.CharField(max_length=200)
    address = models.CharField(max_length=500, blank=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = "Unternehmen"
        verbose_name_plural = "Unternehmen"

    def __str__(self) -> str:
        return self.name


class CustomerUser(models.Model):
    """Model representing a user belonging to a customer company."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    enable_notifications = models.BooleanField(default=False)
    can_handle_contracts = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Kundenbenutzer"
        verbose_name_plural = "Kundenbenutzer"

    def __str__(self) -> str:
        return f'{self.user.username} ({self.company.name})'


class Team(models.Model):
    """Model representing a team within the organization."""

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Team"
        verbose_name_plural = "Teams"

    def __str__(self) -> str:
        return self.name


class TeamMember(models.Model):
    """Model representing a member of a team."""
    class RoleChoices(models.TextChoices):
        TEAMLEITUNG = 'TL', _('Teamleitung')
        DEVELOPER = 'DEV', _('Developer')
        ORGANISATION = 'ORG', _('Organisation')

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team = models.ManyToManyField(Team, blank=True)
    role = models.CharField(max_length=3, choices=RoleChoices.choices, blank=True)

    class Meta:
        verbose_name = "Teammitglied"
        verbose_name_plural = "Teammitglieder"

    def __str__(self) -> str:
        return f'{self.user.username} ({self.team.name})'


class Project(models.Model):
    """Representation of the hosted project.

    This model should only contain a reference to the project and settings.
    """

    class RepositoryServiceTypes(models.IntegerChoices):
            GITLAB = 1, _('GitLab')
            GITHUB = 2, _('GitHub')

    name = models.CharField(max_length=500)
    image = models.ImageField(blank=True)
    public_overview_password = models.CharField(
        max_length=64, default="", null=True, blank=True,
        help_text="Wenn kein Passwort gesetzt ist, ist die öffentliche Übersichtsseite nicht zugänglich"
    )
    public_overview_text = RichTextField(null=True, blank=True)
    first_email_address = models.CharField(
        max_length=200, default=None,
        help_text="E-Mail-Adresse, die benachrichtigt wird, wenn ein neues Ticket vom Kunden erstellt wird"
    )
    enable_documentation = models.BooleanField(
        default=True, help_text="Dokumentation für Benutzer zugänglich machen"
    )
    enable_milestones = models.BooleanField(
        default=True, help_text="Meilensteine visualisieren und ein Gantt-Diagramm erstellen"
    )
    enable_ticket_creation = models.BooleanField(
        default=True, help_text="Kunden erlauben, neue Tickets zu erstellen"
    )
    enable_add_comments = models.BooleanField(
        default=True, help_text="Kunden erlauben, neue Kommentare zu erstellen"
    )
    enable_exports = models.BooleanField(
        default=True, help_text="Benutzern erlauben, Inhalte dieses Projekts herunterzuladen"
    )
    show_system_notes = models.BooleanField(
        default=True, help_text="Systemnotizen zusammen mit Kommentaren anzeigen"
    )
    label_prefix = models.CharField(
        max_length=500, null=True, blank=True,
        help_text="Benutzern ist es nicht erlaubt, Probleme mit Labels zu erstellen, die nicht mit diesem Präfix beginnen"
    )
    wiki_prefix = models.CharField(
        max_length=500, null=True, blank=True,
        help_text="Benutzern ist es nicht erlaubt, Wiki-Seiten mit Pfaden anzuzeigen, die nicht mit diesem Präfix beginnen"
    )
    repositoryService = models.IntegerField(choices=RepositoryServiceTypes.choices, default=RepositoryServiceTypes.GITLAB)
    notification_last_run = models.DateTimeField(default=timezone.now)
    project_identifier = models.CharField(max_length=200)
    private_url_hash = models.CharField(max_length=256, null=True)
    inactive = models.BooleanField(
        default=False, help_text="Inaktive Projekte werden als inaktiv markiert und nicht in der Übersicht angezeigt"
    )
    closed = models.BooleanField(
        default=False, help_text="Wenn geschlossen, ist ein Projekt nicht mehr zugänglich oder sichtbar"
    )
    assignees = models.ManyToManyField('TeamMember', blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    url = models.URLField(null=True, blank=True)

    class Meta:
        verbose_name = "Projekt"
        verbose_name_plural = "Projekte"

    def __str__(self) -> str:
        return f'{self.name} ({self.project_identifier})'

    def public_access_hash(self) -> str:
        if not self.private_url_hash:
            self.private_url_hash = hashlib.md5(
                (settings.SECRET_KEY + self.project_identifier + datetime.datetime.now().strftime(settings.DATETIME_FORMAT)).encode('utf-8')
            ).hexdigest()
            self.save()
        return self.private_url_hash

    def load_remote_project(self):
        # ToDo: add different backends
        if self.repository_service == self.RepositoryServiceTypes.GITLAB:
            from .tools.gitlabCache import loadProject
        elif self.repository_service == self.RepositoryServiceTypes.GITHUB:
            from .tools.githubCache import loadProject
        return loadProject(self, UserProjectAssignment.objects.filter(project=self).first().access_token)


class UserProjectAssignment(models.Model):
    """Assignment between users and projects, containing authentication information (per user token)."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=256)
    enable_notifications = models.BooleanField(default=False)
    teams = models.ManyToManyField(Team, blank=True)

    class Meta:
        verbose_name = "Projektzuweisung"
        verbose_name_plural = "Projektzuweisungen"

    def __str__(self) -> str:
        return f'{self.user.first_name} {self.user.last_name} ({self.project.name})' if self.user else f'{self.project.name}'

    def get_all_users_with_access(self) -> set:
        """Get all users who have access to the project, either directly or through their team."""
        users_with_access = set()
        if self.user:
            users_with_access.add(self.user)
        for team in self.teams.all():
            team_members = TeamMember.objects.filter(team=team)
            for member in team_members:
                users_with_access.add(member.user)
        return users_with_access


class DownloadableFile(models.Model):
    """Files related to a project that can be downloaded by authenticated users with project access."""

    class DownloadableFileTypes(models.IntegerChoices):
        IMPORTANT = -1, _('Wichtige Dateien & Links')
        CLIENT = 0, _('Kundendaten')
        OFFER = 10, _('Angebote')
        DRAFT = 20, _('Entwurf')
        ORDER = 30, _('Bestellungen')
        CONTRACT = 40, _('Verträge')
        PRIVACY = 50, _('Datenschutzdokumente')
        INVOICE = 60, _('Rechnungen')
        DEVELOPMENT = 64, _('Entwicklung')
        PRODUCTION = 65, _('Produktion')
        DOCUMENTATION = 70, _('Dokumentation')
        OTHER = 80, _('Andere')

    name = models.CharField(max_length=200)
    order = models.IntegerField()
    category = models.IntegerField(choices=DownloadableFileTypes.choices)
    file = models.FileField(help_text="Eine herunterladbare Datei - darf nicht hinzugefügt werden, wenn ein Link gesetzt ist", null=True, blank=True)
    link = models.CharField(help_text="Link zu einer Datei oder einem Dokument - darf nicht gesetzt werden, wenn eine Datei vorhanden ist", max_length=2000, null=True, blank=True)
    date = models.DateField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Herunterladbare Datei"
        verbose_name_plural = "Herunterladbare Dateien"

    def __str__(self) -> str:
        return f'{self.name} ({self.project.name})'

    def extension(self) -> str:
        name, extension = os.path.splitext(self.file.name)
        return extension[1:].upper()