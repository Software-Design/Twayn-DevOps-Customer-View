# Generated by Django 4.1 on 2022-11-10 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userinterface', '0021_alter_downloadablefile_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='inactive',
            field=models.BooleanField(default=False, help_text='Inatvie project are marked as inactive and not shown in the overview'),
        ),
    ]
