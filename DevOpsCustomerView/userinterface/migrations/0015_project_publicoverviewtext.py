# Generated by Django 4.1 on 2022-10-27 13:46

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userinterface', '0014_project_privateurlhash'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='publicOverviewText',
            field=ckeditor.fields.RichTextField(default=''),
            preserve_default=False,
        ),
    ]