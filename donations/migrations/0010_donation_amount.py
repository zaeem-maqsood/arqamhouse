# Generated by Django 2.2 on 2020-05-09 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0009_donation_anonymous'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True),
        ),
    ]