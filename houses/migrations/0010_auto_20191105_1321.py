# Generated by Django 2.2.6 on 2019-11-05 18:21

from django.db import migrations, models
import houses.models


class Migration(migrations.Migration):

    dependencies = [
        ('houses', '0009_auto_20191105_1319'),
    ]

    operations = [
        migrations.AlterField(
            model_name='housedirector',
            name='back_id',
            field=models.FileField(upload_to=houses.models.id_location),
        ),
        migrations.AlterField(
            model_name='housedirector',
            name='front_id',
            field=models.FileField(upload_to=houses.models.id_location),
        ),
    ]
