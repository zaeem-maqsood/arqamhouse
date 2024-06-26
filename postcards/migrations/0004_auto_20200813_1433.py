# Generated by Django 2.2 on 2020-08-13 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('postcards', '0003_auto_20200727_1944'),
    ]

    operations = [
        migrations.AddField(
            model_name='postcardorder',
            name='recipient_administrative_area_level_1',
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='postcardorder',
            name='recipient_locality',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='postcardorder',
            name='recipient_route',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='postcardorder',
            name='recipient_street_number',
            field=models.PositiveIntegerField(blank=True, max_length=10, null=True),
        ),
    ]
