# Generated by Django 2.2.5 on 2019-10-02 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0020_eventorder_public_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventorder',
            name='number',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]
