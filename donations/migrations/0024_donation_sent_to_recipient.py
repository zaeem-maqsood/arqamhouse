# Generated by Django 2.2 on 2020-06-09 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0023_donationtype_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='sent_to_recipient',
            field=models.BooleanField(default=False),
        ),
    ]
