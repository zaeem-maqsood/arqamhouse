# Generated by Django 2.2 on 2020-03-28 21:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0070_eventlive_facing_mode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventlive',
            name='facing_mode',
            field=models.CharField(blank=True, choices=[('user', 'User'), ('environment', 'Environment'), ('screen', 'Screen')], max_length=150, null=True),
        ),
    ]
