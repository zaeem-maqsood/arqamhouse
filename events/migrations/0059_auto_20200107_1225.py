# Generated by Django 2.2 on 2020-01-07 17:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0058_eventorder_checkins'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='checkin',
            name='confirmation_message',
        ),
        migrations.RemoveField(
            model_name='checkin',
            name='send_confirmation',
        ),
    ]
