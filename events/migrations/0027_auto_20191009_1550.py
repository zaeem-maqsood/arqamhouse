# Generated by Django 2.2.5 on 2019-10-09 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0026_auto_20191009_1547'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventdiscount',
            name='total_uses',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
