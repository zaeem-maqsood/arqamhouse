# Generated by Django 2.2 on 2020-01-06 21:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0055_checkin_attendees'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='checkin',
            name='attendees',
        ),
    ]
