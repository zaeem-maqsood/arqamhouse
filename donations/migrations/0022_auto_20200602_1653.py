# Generated by Django 2.2 on 2020-06-02 20:53

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0021_donation_gift_donation_item_amount'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='donationtype',
            options={'ordering': ['-created_at', '-updated_at']},
        ),
        migrations.AddField(
            model_name='donationtype',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='donationtype',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]