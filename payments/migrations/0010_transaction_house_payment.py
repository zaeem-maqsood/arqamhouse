# Generated by Django 2.2.4 on 2019-09-09 17:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0009_housebalancelog_opening_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='house_payment',
            field=models.BooleanField(default=False),
        ),
    ]