# Generated by Django 2.2.5 on 2019-10-10 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0030_auto_20191010_1547'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventcartitem',
            name='discount_code_activated',
            field=models.BooleanField(default=False),
        ),
    ]
