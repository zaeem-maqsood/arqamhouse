# Generated by Django 2.2 on 2020-02-06 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0063_auto_20200128_1307'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='send_to_subscribers',
            field=models.BooleanField(default=True),
        ),
    ]
