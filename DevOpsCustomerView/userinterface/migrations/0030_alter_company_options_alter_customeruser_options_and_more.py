# Generated by Django 4.2.16 on 2024-10-08 13:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userinterface', '0029_alter_downloadablefile_category_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='company',
            options={'verbose_name': 'Unternehmen', 'verbose_name_plural': 'Unternehmen'},
        ),
        migrations.AlterModelOptions(
            name='customeruser',
            options={'verbose_name': 'Kundenbenutzer', 'verbose_name_plural': 'Kundenbenutzer'},
        ),
        migrations.AlterModelOptions(
            name='downloadablefile',
            options={'verbose_name': 'Herunterladbare Datei', 'verbose_name_plural': 'Herunterladbare Dateien'},
        ),
        migrations.AlterModelOptions(
            name='project',
            options={'verbose_name': 'Projekt', 'verbose_name_plural': 'Projekte'},
        ),
        migrations.AlterModelOptions(
            name='team',
            options={'verbose_name': 'Team', 'verbose_name_plural': 'Teams'},
        ),
        migrations.AlterModelOptions(
            name='teammember',
            options={'verbose_name': 'Teammitglied', 'verbose_name_plural': 'Teammitglieder'},
        ),
        migrations.AlterModelOptions(
            name='userprojectassignment',
            options={'verbose_name': 'Benutzerprojektzuweisung', 'verbose_name_plural': 'Benutzerprojektzuweisungen'},
        ),
    ]
