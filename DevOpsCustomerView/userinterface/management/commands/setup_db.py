import os
import django
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from userinterface.models import Company, CustomerUser, Project, Team, TeamMember

django.setup()

class Command(BaseCommand):
    help = 'Setup the database with default values'

    def handle(self, *args, **kwargs) -> None:
        try:
            self.stdout.write("Alte Datenbank löschen...")
            self.delete_old_database()

            self.stdout.write("Migrationen ausführen...")
            self.run_migrations()

            self.stdout.write("Standardteam erstellen...")
            default_team = self.create_default_team()

            self.stdout.write("Standardunternehmen erstellen...")
            default_company = self.create_default_company()

            self.stdout.write("Standard-Admin-Benutzer erstellen...")
            default_admin_user = self.create_default_admin_user(default_team)

            self.stdout.write("Standardprojekt erstellen...")
            default_project = self.create_default_project(default_company, default_team)

            self.stdout.write("Standardbenutzer für das Unternehmen erstellen...")
            self.create_default_company_users(default_company)

            self.stdout.write(self.style.SUCCESS("Setup abgeschlossen."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Fehler während des Setups: {e}"))

    def delete_old_database(self) -> None:
        db_path = settings.DATABASES['default']['NAME']
        if os.path.exists(db_path):
            os.remove(db_path)
            self.stdout.write(self.style.SUCCESS(f"Alte Datenbank gelöscht unter {db_path}"))
        else:
            self.stdout.write(self.style.WARNING(f"Keine Datenbank gefunden unter {db_path}"))

    def run_migrations(self) -> None:
        call_command('makemigrations')
        call_command('migrate')

    def create_default_team(self) -> Team:
        team, _ = Team.objects.get_or_create(
            name='Kreatives Software Team GmbH',
            defaults={'description': 'Internes Team für Kreatives Software Team GmbH.'}
        )
        return team

    def create_default_company(self) -> Company:
        company, _ = Company.objects.get_or_create(
            name='Innovative Lösungen AG',
            defaults={
                'address': '123 Innovationsstraße, Kreativstadt, KS 12345',
                'contact_email': 'pm+company@software-design.de',
                'contact_phone': '123-456-7890'
            }
        )
        return company

    def create_default_admin_user(self, team: Team) -> User:
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'pm+admin@software-design.de',
                'first_name': 'Admin',
                'last_name': 'Benutzer',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user.set_password('admin')
            user.save()

        TeamMember.objects.get_or_create(
            user=user,
            team=team,
            defaults={'role': 'Admin'}
        )
        return user

    def create_default_project(self, company: Company, team: Team) -> Project:
        project, created = Project.objects.get_or_create(
            name='Innovatives Projekt',
            defaults={
                'repository_service': Project.RepositoryServiceTypes.GITLAB,
                'url': 'https://gitlab.com/innovativesprojekt',
                'company': company,
                'first_email_address': 'pm+project@software-design.de',
                'project_identifier': 'innovatives-projekt',
                'inactive': False,
                'closed': False
            }
        )
        if created:
            project.assignees.add(*team.teammember_set.all())
        return project

    def create_default_company_users(self, company: Company) -> None:
        users_data = [
            {
                'username': 'user1',
                'email': 'pm+user1@software-design.de',
                'first_name': 'Benutzer',
                'last_name': 'Eins'
            },
            {
                'username': 'user2',
                'email': 'pm+user2@software-design.de',
                'first_name': 'Benutzer',
                'last_name': 'Zwei'
            }
        ]

        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_staff': False,
                    'is_superuser': False
                }
            )
            if created:
                user.set_password('password')
                user.save()

            CustomerUser.objects.get_or_create(
                user=user,
                company=company
            )