# Generated by Django 2.2 on 2020-11-17 20:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0009_auto_20201113_1949'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='address',
            new_name='old_address',
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(blank=True, max_length=200, null=True)),
                ('apt_number', models.CharField(blank=True, max_length=20, null=True)),
                ('street_number', models.CharField(blank=True, max_length=20, null=True)),
                ('route', models.CharField(blank=True, max_length=100, null=True)),
                ('locality', models.CharField(blank=True, max_length=100, null=True)),
                ('administrative_area_level_1', models.CharField(blank=True, max_length=4, null=True)),
                ('postal_code', models.CharField(blank=True, max_length=10, null=True)),
                ('profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]