# Generated by Django 2.2 on 2020-08-18 01:45

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('postcards', '0006_auto_20200813_1613'),
    ]

    operations = [
        migrations.AddField(
            model_name='postcardorder',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
