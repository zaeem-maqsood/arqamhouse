# Generated by Django 2.2 on 2020-02-06 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0064_event_send_to_subscribers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='send_to_subscribers',
            field=models.BooleanField(default=False),
        ),
    ]