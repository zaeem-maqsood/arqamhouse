# Generated by Django 2.2 on 2020-11-19 04:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0011_address_default'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='name',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]