# Generated by Django 2.2.5 on 2019-09-25 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0018_eventcart_house_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventorder',
            name='house_created',
            field=models.BooleanField(default=False),
        ),
    ]
