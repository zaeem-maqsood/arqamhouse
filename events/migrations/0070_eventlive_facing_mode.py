# Generated by Django 2.2 on 2020-03-26 02:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0069_eventlive'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventlive',
            name='facing_mode',
            field=models.CharField(blank=True, choices=[('user', 'User'), ('environment', 'Environment')], max_length=150, null=True),
        ),
    ]