# Generated by Django 2.2 on 2020-06-03 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0100_eventlivefee_broadcasted_mins'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventlivearchive',
            name='name',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
    ]
