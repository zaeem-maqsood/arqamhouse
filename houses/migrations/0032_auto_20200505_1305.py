# Generated by Django 2.2 on 2020-05-05 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('houses', '0031_house_campaign_view_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='house',
            name='campaign_view_score',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='house',
            name='donation_score',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='house',
            name='event_score',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]