# Generated by Django 2.2.5 on 2019-10-09 20:36

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0028_auto_20191009_1617'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventdiscount',
            name='code',
            field=models.CharField(blank=True, max_length=100, null=True, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')]),
        ),
    ]
