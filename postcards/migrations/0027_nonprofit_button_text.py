# Generated by Django 2.2 on 2020-12-27 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('postcards', '0026_auto_20201108_2008'),
    ]

    operations = [
        migrations.AddField(
            model_name='nonprofit',
            name='button_text',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]