# Generated by Django 4.1.2 on 2022-12-22 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userinterface', '0023_project_firstemailadress'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='firstEMailAdress',
        ),
        migrations.AddField(
            model_name='project',
            name='firstEMailAddress',
            field=models.CharField(default=None, help_text='E-Mail Address that gets notified if a new ticket is created by the custome', max_length=100, null=True),
        ),
    ]
