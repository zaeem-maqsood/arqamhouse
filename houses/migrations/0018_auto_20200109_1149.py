# Generated by Django 2.2 on 2020-01-09 16:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('houses', '0017_auto_20200109_1148'),
    ]

    operations = [
        migrations.RenameField(
            model_name='house',
            old_name='legal_business_name',
            new_name='legal_name',
        ),
    ]
