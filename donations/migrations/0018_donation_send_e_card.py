# Generated by Django 2.2 on 2020-05-26 21:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0017_auto_20200526_1737'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='send_e_card',
            field=models.BooleanField(default=False),
        ),
    ]