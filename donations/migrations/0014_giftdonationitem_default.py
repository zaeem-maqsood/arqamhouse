# Generated by Django 2.2 on 2020-05-26 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0013_giftdonationitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='giftdonationitem',
            name='default',
            field=models.BooleanField(default=False),
        ),
    ]
