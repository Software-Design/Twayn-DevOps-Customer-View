# Generated by Django 4.1 on 2022-11-09 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userinterface', '0020_downloadablefile_link_alter_downloadablefile_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='downloadablefile',
            name='category',
            field=models.IntegerField(choices=[(-1, 'Important Files & Links'), (0, 'Customer data'), (10, 'Offers'), (20, 'Draft'), (30, 'Orders'), (40, 'Contracts'), (50, 'Privacy documents'), (60, 'Invoices'), (64, 'Development'), (65, 'Production'), (70, 'Documentation'), (80, 'Other')], max_length=200),
        ),
    ]
