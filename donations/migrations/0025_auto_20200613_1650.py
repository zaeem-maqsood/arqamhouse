# Generated by Django 2.2 on 2020-06-13 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0024_donation_sent_to_recipient'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donation',
            name='name',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]