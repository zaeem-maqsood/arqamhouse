# Generated by Django 2.2 on 2020-11-21 22:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipients', '0005_recipient_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipient',
            name='order',
        ),
    ]
