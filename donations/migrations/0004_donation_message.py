# Generated by Django 2.2 on 2020-04-20 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0003_donationtype_general_donation'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='message',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
