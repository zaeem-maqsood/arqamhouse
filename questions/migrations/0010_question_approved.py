# Generated by Django 2.0.3 on 2018-07-04 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0009_auto_20180704_1813'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='approved',
            field=models.BooleanField(default=True),
        ),
    ]
