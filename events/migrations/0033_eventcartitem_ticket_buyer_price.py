# Generated by Django 2.2.5 on 2019-10-11 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0032_auto_20191011_1235'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventcartitem',
            name='ticket_buyer_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True),
        ),
    ]
