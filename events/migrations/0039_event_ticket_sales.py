# Generated by Django 2.2.6 on 2019-10-31 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0038_eventcart_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='ticket_sales',
            field=models.BooleanField(default=True),
        ),
    ]