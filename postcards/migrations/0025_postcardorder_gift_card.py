# Generated by Django 2.2 on 2020-11-02 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('postcards', '0024_auto_20201101_2129'),
    ]

    operations = [
        migrations.AddField(
            model_name='postcardorder',
            name='gift_card',
            field=models.CharField(blank=True, choices=[('Apple', 'Apple'), ('Google', 'Google'), ('HomeSense', 'HomeSense'), ('Amazon', 'Amazon'), ('Indigo', 'Indigo'), ('Shoppers', 'Shoppers')], max_length=150, null=True),
        ),
    ]
