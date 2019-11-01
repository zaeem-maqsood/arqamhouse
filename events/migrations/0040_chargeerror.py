# Generated by Django 2.2.6 on 2019-11-01 17:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0039_event_ticket_sales'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChargeError',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_id', models.CharField(blank=True, max_length=150, null=True)),
                ('failed', models.BooleanField(default=False)),
                ('code_fail_reason', models.CharField(blank=True, max_length=250, null=True)),
                ('failure_code', models.CharField(blank=True, max_length=150, null=True)),
                ('failure_message', models.CharField(blank=True, max_length=150, null=True)),
                ('outcome_type', models.CharField(blank=True, max_length=150, null=True)),
                ('network_status', models.CharField(blank=True, max_length=150, null=True)),
                ('reason', models.CharField(blank=True, max_length=150, null=True)),
                ('name', models.CharField(blank=True, max_length=250, null=True)),
                ('email', models.EmailField(max_length=300)),
                ('event_cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.EventCart')),
            ],
        ),
    ]
