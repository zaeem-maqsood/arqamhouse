# Generated by Django 2.2.4 on 2019-08-21 20:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0014_auto_20190821_2004'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventorder',
            name='qrcode',
        ),
    ]
