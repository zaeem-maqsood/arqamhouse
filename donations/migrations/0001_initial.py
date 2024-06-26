# Generated by Django 2.2 on 2020-04-17 19:23

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('houses', '0024_house_free_live_video'),
        ('payments', '0033_auto_20200415_1510'),
    ]

    operations = [
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(blank=True, max_length=150, null=True)),
                ('email', models.EmailField(max_length=300)),
                ('address', models.CharField(blank=True, max_length=200, null=True)),
                ('postal_code', models.CharField(blank=True, max_length=6, null=True)),
                ('issue_receipt', models.BooleanField(default=False)),
                ('receipt_number', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('house', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='houses.House')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payments.Transaction')),
            ],
            options={
                'ordering': ['-created_at', '-updated_at'],
                'abstract': False,
            },
        ),
    ]
