# Generated by Django 2.2 on 2020-05-17 21:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0010_donation_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donation',
            name='postal_code',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]