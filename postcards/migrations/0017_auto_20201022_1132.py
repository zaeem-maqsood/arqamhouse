# Generated by Django 2.2 on 2020-10-22 15:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('postcards', '0016_postcardorder_promo_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postcardorder',
            name='promo_code',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='postcards.PromoCode'),
        ),
    ]
