# Generated by Django 2.2 on 2020-01-28 18:07

from django.db import migrations, models
import events.models.orders


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0062_event_ics_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='ics_file',
        ),
        migrations.AddField(
            model_name='eventorder',
            name='ics_file',
            field=models.FileField(blank=True, null=True, upload_to=events.models.orders.ics_file_location),
        ),
    ]
