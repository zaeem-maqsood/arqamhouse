# Generated by Django 2.1 on 2019-03-11 00:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cities_light', '0008_city_timezone'),
        ('profiles', '0003_auto_20180827_0228'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='timezone',
        ),
        migrations.AddField(
            model_name='profile',
            name='city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cities_light.City'),
        ),
        migrations.AddField(
            model_name='profile',
            name='region',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cities_light.Region'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='country',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cities_light.Country'),
        ),
    ]
