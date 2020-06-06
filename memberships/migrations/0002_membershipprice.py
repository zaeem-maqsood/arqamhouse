# Generated by Django 2.2 on 2020-05-17 07:14

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MembershipPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('currency', models.CharField(blank=True, max_length=10, null=True)),
                ('interval', models.CharField(blank=True, choices=[('day', 'day'), ('week', 'week'), ('month', 'month'), ('year', 'year')], max_length=150, null=True)),
                ('interval_count', models.PositiveIntegerField(blank=True, default=1, null=True)),
                ('membership_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='memberships.MembershipProduct')),
            ],
            options={
                'ordering': ['-created_at', '-updated_at'],
                'abstract': False,
            },
        ),
    ]