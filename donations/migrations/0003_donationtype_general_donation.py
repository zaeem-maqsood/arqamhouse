# Generated by Django 2.2 on 2020-04-20 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0002_auto_20200420_1342'),
    ]

    operations = [
        migrations.AddField(
            model_name='donationtype',
            name='general_donation',
            field=models.BooleanField(default=False),
        ),
    ]
