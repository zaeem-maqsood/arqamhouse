# Generated by Django 2.2 on 2019-12-19 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0050_eventrefundrequest_dismissed'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendee',
            name='unique_id',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
    ]
