# Generated by Django 2.2 on 2020-05-05 16:53

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscribers', '0020_auto_20200505_1235'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriber',
            name='campaign_view_score',
            field=models.PositiveIntegerField(blank=True, default=100, null=True),
        ),
        migrations.AddField(
            model_name='subscriber',
            name='campaign_views',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='subscriber',
            name='donation_amount_score',
            field=models.PositiveIntegerField(blank=True, default=100, null=True),
        ),
        migrations.AddField(
            model_name='subscriber',
            name='donation_score',
            field=models.PositiveIntegerField(blank=True, default=100, null=True),
        ),
        migrations.AddField(
            model_name='subscriber',
            name='event_attendance',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='subscriber',
            name='event_score',
            field=models.PositiveIntegerField(blank=True, default=100, null=True),
        ),
        migrations.AddField(
            model_name='subscriber',
            name='highest_amount_donated',
            field=models.DecimalField(blank=True, decimal_places=2, default=Decimal('0.00'), max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='subscriber',
            name='times_donated',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]