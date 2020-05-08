# Generated by Django 2.2 on 2020-05-05 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('houses', '0028_house_charitable_registration_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='house',
            name='donation_amount_score',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='house',
            name='donation_score',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='house',
            name='event_score',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]