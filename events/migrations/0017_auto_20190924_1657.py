# Generated by Django 2.2.5 on 2019-09-24 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0016_eventcartitem_pay'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventcartitem',
            name='pay',
        ),
        migrations.AddField(
            model_name='eventcart',
            name='pay',
            field=models.BooleanField(default=True),
        ),
    ]