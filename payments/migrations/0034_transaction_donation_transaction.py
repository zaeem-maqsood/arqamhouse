# Generated by Django 2.2 on 2020-04-18 21:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0033_auto_20200415_1510'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='donation_transaction',
            field=models.BooleanField(default=False),
        ),
    ]
