# Generated by Django 2.2 on 2020-02-20 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0065_auto_20200206_1233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendee',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]