# Generated by Django 2.2 on 2020-01-17 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('houses', '0019_house_logo'),
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='subscribed_houses',
            field=models.ManyToManyField(blank=True, related_name='subscribed_houses', to='houses.House'),
        ),
    ]
