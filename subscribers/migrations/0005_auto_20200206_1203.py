# Generated by Django 2.2 on 2020-02-06 17:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscribers', '0004_auto_20200125_1703'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subscriber',
            old_name='attendance_subtractor',
            new_name='attendance_total',
        ),
        migrations.RenameField(
            model_name='subscriber',
            old_name='engagement_subtractor',
            new_name='engagement_total',
        ),
    ]
