# Generated by Django 4.2.16 on 2024-10-08 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userinterface', '0028_project_company_project_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='downloadablefile',
            name='category',
            field=models.IntegerField(choices=[(-1, 'Wichtige Dateien & Links'), (0, 'Kundendaten'), (10, 'Angebote'), (20, 'Entwurf'), (30, 'Bestellungen'), (40, 'Verträge'), (50, 'Datenschutzdokumente'), (60, 'Rechnungen'), (64, 'Entwicklung'), (65, 'Produktion'), (70, 'Dokumentation'), (80, 'Andere')]),
        ),
        migrations.AlterField(
            model_name='downloadablefile',
            name='file',
            field=models.FileField(blank=True, help_text='Eine herunterladbare Datei - darf nicht hinzugefügt werden, wenn ein Link gesetzt ist', null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='downloadablefile',
            name='link',
            field=models.CharField(blank=True, help_text='Link zu einer Datei oder einem Dokument - darf nicht gesetzt werden, wenn eine Datei vorhanden ist', max_length=2000, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='closed',
            field=models.BooleanField(default=False, help_text='Wenn geschlossen, ist ein Projekt nicht mehr zugänglich oder sichtbar'),
        ),
        migrations.AlterField(
            model_name='project',
            name='enable_add_comments',
            field=models.BooleanField(default=True, help_text='Kunden erlauben, neue Kommentare zu erstellen'),
        ),
        migrations.AlterField(
            model_name='project',
            name='enable_documentation',
            field=models.BooleanField(default=True, help_text='Dokumentation für Benutzer zugänglich machen'),
        ),
        migrations.AlterField(
            model_name='project',
            name='enable_exports',
            field=models.BooleanField(default=True, help_text='Benutzern erlauben, Inhalte dieses Projekts herunterzuladen'),
        ),
        migrations.AlterField(
            model_name='project',
            name='enable_milestones',
            field=models.BooleanField(default=True, help_text='Meilensteine visualisieren und ein Gantt-Diagramm erstellen'),
        ),
        migrations.AlterField(
            model_name='project',
            name='enable_ticket_creation',
            field=models.BooleanField(default=True, help_text='Kunden erlauben, neue Tickets zu erstellen'),
        ),
        migrations.AlterField(
            model_name='project',
            name='first_email_address',
            field=models.CharField(default=None, help_text='E-Mail-Adresse, die benachrichtigt wird, wenn ein neues Ticket vom Kunden erstellt wird', max_length=200),
        ),
        migrations.AlterField(
            model_name='project',
            name='inactive',
            field=models.BooleanField(default=False, help_text='Inaktive Projekte werden als inaktiv markiert und nicht in der Übersicht angezeigt'),
        ),
        migrations.AlterField(
            model_name='project',
            name='label_prefix',
            field=models.CharField(blank=True, help_text='Benutzern ist es nicht erlaubt, Probleme mit Labels zu erstellen, die nicht mit diesem Präfix beginnen', max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='public_overview_password',
            field=models.CharField(blank=True, default='', help_text='Wenn kein Passwort gesetzt ist, ist die öffentliche Übersichtsseite nicht zugänglich', max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='show_system_notes',
            field=models.BooleanField(default=True, help_text='Systemnotizen zusammen mit Kommentaren anzeigen'),
        ),
        migrations.AlterField(
            model_name='project',
            name='wiki_prefix',
            field=models.CharField(blank=True, help_text='Benutzern ist es nicht erlaubt, Wiki-Seiten mit Pfaden anzuzeigen, die nicht mit diesem Präfix beginnen', max_length=500, null=True),
        ),
    ]
