# Generated by Django 2.2 on 2020-06-06 23:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0022_auto_20200602_1653'),
    ]

    operations = [
        migrations.AddField(
            model_name='donationtype',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
