# Generated by Django 2.2 on 2020-11-21 22:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0012_address_name'),
        ('orders', '0006_order_total_donation_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='lineorder',
            name='sender_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='profiles.Address'),
        ),
    ]
