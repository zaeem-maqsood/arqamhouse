# Generated by Django 2.2.5 on 2019-09-23 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0019_auto_20190919_2222'),
    ]

    operations = [
        migrations.AddField(
            model_name='refund',
            name='house_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True),
        ),
    ]
