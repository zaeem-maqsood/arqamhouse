# Generated by Django 2.2.4 on 2019-09-10 18:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0014_auto_20190910_1307'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='etransfer',
            name='payout_setting',
        ),
        migrations.AddField(
            model_name='payoutsetting',
            name='etransfer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='payments.Etransfer'),
        ),
    ]
