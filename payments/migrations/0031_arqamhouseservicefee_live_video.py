# Generated by Django 2.2 on 2020-04-13 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0030_auto_20200413_1532'),
    ]

    operations = [
        migrations.AddField(
            model_name='arqamhouseservicefee',
            name='live_video',
            field=models.BooleanField(default=False),
        ),
    ]
