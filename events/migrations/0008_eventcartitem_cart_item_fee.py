# Generated by Django 2.2.4 on 2019-09-04 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_auto_20190903_1628'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventcartitem',
            name='cart_item_fee',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True),
        ),
    ]
