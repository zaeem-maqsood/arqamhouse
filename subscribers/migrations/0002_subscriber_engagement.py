# Generated by Django 2.2 on 2020-01-23 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscribers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriber',
            name='engagement',
            field=models.CharField(blank=True, choices=[('Often', 'often'), ('Sometimes', 'Sometimes'), ('Rarely', 'Rarely')], max_length=150, null=True),
        ),
    ]
