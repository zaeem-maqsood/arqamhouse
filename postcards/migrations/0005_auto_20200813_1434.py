# Generated by Django 2.2 on 2020-08-13 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('postcards', '0004_auto_20200813_1433'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postcardorder',
            name='recipient_street_number',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
