# Generated by Django 2.2.4 on 2019-09-05 16:19

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_auto_20190903_1451'),
    ]

    operations = [
        migrations.AddField(
            model_name='refund',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True),
        ),
    ]
