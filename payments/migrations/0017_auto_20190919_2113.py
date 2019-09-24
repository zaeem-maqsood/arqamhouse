# Generated by Django 2.2.5 on 2019-09-20 01:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0016_auto_20190910_1628'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankTransfer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transit', models.PositiveIntegerField()),
                ('institution', models.PositiveIntegerField()),
                ('account', models.PositiveIntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='payoutsetting',
            name='bank_transfer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='payments.BankTransfer'),
        ),
    ]
