# Generated by Django 2.2 on 2020-02-08 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscribers', '0009_campaign_house'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='draft',
            field=models.BooleanField(default=True),
        ),
    ]
