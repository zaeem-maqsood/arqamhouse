# Generated by Django 2.2 on 2020-11-16 23:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_auto_20201116_1751'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='total_donation_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True),
        ),
    ]