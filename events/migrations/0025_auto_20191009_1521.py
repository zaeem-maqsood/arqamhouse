# Generated by Django 2.2.5 on 2019-10-09 19:21

from django.db import migrations


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('events', '0024_eventdiscounts'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='EventDiscounts',
            new_name='EventDiscount',
        ),
    ]
