# Generated by Django 2.2.7 on 2019-12-11 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0025_auto_20191205_1246'),
    ]

    operations = [
        migrations.AddField(
            model_name='housebalance',
            name='gross_balance',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name='housebalancelog',
            name='gross_balance',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
    ]
