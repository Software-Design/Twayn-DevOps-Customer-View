import os
import django
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand
from typing import Dict
from userinterface.models import (
    CustomerCompany,
    CustomerUser,
    Project,
    Team,
    TeamMember,
)

django.setup()


class Command(BaseCommand):
    help = "Setup the database with default values"

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
            default_project = self.create_default_project(
                default_company, default_team, default_admin_user
            )

            self.stdout.write("Standardbenutzer für das Unternehmen erstellen...")
            self.create_default_customer_company_users(default_company)

            self.stdout.write(self.style.SUCCESS("Setup abgeschlossen."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Fehler während des Setups: {e}"))

    def delete_old_database(self) -> None:
        db_path = settings.DATABASES["default"]["NAME"]
        if os.path.exists(db_path):
            os.remove(db_path)
            self.stdout.write(
                self.style.SUCCESS(f"Alte Datenbank gelöscht unter {db_path}")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"Keine Datenbank gefunden unter {db_path}")
            )

    def run_migrations(self) -> None:
        call_command("makemigrations")
        call_command("migrate")
        call_command("createcachetable")

    def create_default_team(self) -> Team:
        team, _ = Team.objects.get_or_create(
            name="SD Team Web", defaults={"description": "Internes Team für Webseiten."}
        )
        return team

    def create_default_company(self) -> CustomerCompany:
        customer_company, _ = CustomerCompany.objects.get_or_create(
            name="Fischer Rista AG",
            defaults={
                "address": "123 Innovationsstraße, Kreativstadt, KS 12345",
                "contact_email": "pm+company@software-design.de",
                "contact_phone": "123-456-7890",
            },
        )
        return customer_company

    def create_default_admin_user(self, team: Team) -> User:
        user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "pm+admin@software-design.de",
                "first_name": "Admin",
                "last_name": "Benutzer",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            user.set_password("admin")
            user.save()

        # Ensure the admin user is added to the team
        TeamMember.objects.get_or_create(user=user, team=team, defaults={"role": "TL"})
        return user

    def create_default_project(
        self, customer_company: CustomerCompany, team: Team, admin_user: User
    ) -> Project:
        project_defaults: Dict[str, object] = {
            "repository_service": Project.RepositoryServiceTypes.GITHUB,
            "url": "https://github.com/SD-Software-Design-GmbH/SD-Twayn",
            "access_token": "",
            "customer_company": customer_company,
            "first_email_address": "pm+project@software-design.de",
            "project_identifier": "866492438",
            "inactive": False,
            "closed": False,
        }

        project, created = Project.objects.get_or_create(
            name="Twayn Projekt",
            defaults=project_defaults,
        )

        if created:
            project.teams.set([team.id])

        return project

    def create_default_customer_company_users(
        self, customer_company: CustomerCompany
    ) -> None:
        users_data = [
            {
                "username": "user1",
                "email": "pm+user1@software-design.de",
                "first_name": "Benutzer",
                "last_name": "Eins",
            },
            {
                "username": "user2",
                "email": "pm+user2@software-design.de",
                "first_name": "Benutzer",
                "last_name": "Zwei",
            },
        ]

        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data["username"],
                defaults={
                    "email": user_data["email"],
                    "first_name": user_data["first_name"],
                    "last_name": user_data["last_name"],
                    "is_staff": False,
                    "is_superuser": False,
                },
            )
            if created:
                user.set_password("password")
                user.save()

            CustomerUser.objects.get_or_create(
                user=user, customer_company=customer_company
            )
