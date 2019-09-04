# Generated by Django 2.2.4 on 2019-09-03 15:47

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('houses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payout',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
                ('house', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='houses.House')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('payment_id', models.CharField(blank=True, max_length=150, null=True)),
                ('failed', models.BooleanField(default=False)),
                ('partial_refunded', models.BooleanField(default=False)),
                ('refunded', models.BooleanField(default=False)),
                ('code_fail_reason', models.CharField(blank=True, max_length=250, null=True)),
                ('failure_code', models.CharField(blank=True, max_length=150, null=True)),
                ('failure_message', models.CharField(blank=True, max_length=150, null=True)),
                ('last_four', models.CharField(blank=True, max_length=10, null=True)),
                ('brand', models.CharField(blank=True, max_length=100, null=True)),
                ('network_status', models.CharField(blank=True, max_length=150, null=True)),
                ('reason', models.CharField(blank=True, max_length=150, null=True)),
                ('risk_level', models.CharField(blank=True, max_length=150, null=True)),
                ('seller_message', models.CharField(blank=True, max_length=150, null=True)),
                ('outcome_type', models.CharField(blank=True, max_length=150, null=True)),
                ('name', models.CharField(blank=True, max_length=250, null=True)),
                ('address_line_1', models.CharField(blank=True, max_length=150, null=True)),
                ('address_state', models.CharField(blank=True, max_length=150, null=True)),
                ('address_postal_code', models.CharField(blank=True, max_length=150, null=True)),
                ('address_city', models.CharField(blank=True, max_length=150, null=True)),
                ('address_country', models.CharField(blank=True, max_length=150, null=True)),
                ('house', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='houses.House')),
                ('payout', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='payments.Payout')),
            ],
        ),
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payments.Transaction')),
            ],
        ),
    ]
