# Generated by Django 2.2.5 on 2019-09-20 01:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0017_auto_20190919_2113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banktransfer',
            name='account',
            field=models.CharField(max_length=7),
        ),
        migrations.AlterField(
            model_name='banktransfer',
            name='institution',
            field=models.CharField(max_length=3),
        ),
        migrations.AlterField(
            model_name='banktransfer',
            name='transit',
            field=models.CharField(max_length=5),
        ),
    ]
