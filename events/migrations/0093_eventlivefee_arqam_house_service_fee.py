# Generated by Django 2.2 on 2020-04-13 19:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0092_auto_20200413_1532'),
        ('payments', '0030_auto_20200413_1532'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventlivefee',
            name='arqam_house_service_fee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='payments.ArqamHouseServiceFee'),
        ),
    ]
