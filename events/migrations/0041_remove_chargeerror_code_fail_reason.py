# Generated by Django 2.2.6 on 2019-11-01 17:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0040_chargeerror'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chargeerror',
            name='code_fail_reason',
        ),
    ]
