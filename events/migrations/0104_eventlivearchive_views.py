# Generated by Django 2.2 on 2020-06-03 21:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0103_auto_20200603_1601'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventlivearchive',
            name='views',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]
