# Generated by Django 2.0.3 on 2018-08-08 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0011_remove_attendeegeneralquestions_gender_required'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendeegeneralquestions',
            name='name',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='attendeegeneralquestions',
            name='name_required',
            field=models.BooleanField(default=True),
        ),
    ]
