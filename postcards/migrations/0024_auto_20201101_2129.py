# Generated by Django 2.2 on 2020-11-02 02:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('postcards', '0023_auto_20201031_2022'),
    ]

    operations = [
        migrations.AddField(
            model_name='postcardorder',
            name='add_gift_card',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='postcardorder',
            name='gift_card_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True),
        ),
    ]
