# Generated by Django 4.1 on 2022-09-01 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userinterface', '0003_project_labelprefix_project_wikiprefix'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='labelPrefix',
            field=models.CharField(blank=True, help_text="User are not allowed to create issues with labels that don't start with this prefix", max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='wikiPrefix',
            field=models.CharField(blank=True, help_text="User are not allowed to view wiki pages with paths that don't start with this prefix", max_length=500, null=True),
        ),
    ]