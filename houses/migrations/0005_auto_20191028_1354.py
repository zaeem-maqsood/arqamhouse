# Generated by Django 2.2.6 on 2019-10-28 17:54

import arqamhouse.aws.utils
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import houses.models


class Migration(migrations.Migration):

    dependencies = [
        ('houses', '0004_auto_20190924_1143'),
    ]

    operations = [
        migrations.AddField(
            model_name='house',
            name='address',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='house',
            name='house_type',
            field=models.CharField(choices=[('individual', 'Individual'), ('company', 'Company'), ('nonprofit', 'Nonprofit')], default='individual', max_length=150),
        ),
        migrations.AddField(
            model_name='house',
            name='ip_address',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='house',
            name='postal_code',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
        migrations.AddField(
            model_name='house',
            name='verified',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='HouseDirector',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('dob_year', models.PositiveIntegerField(blank=True, null=True)),
                ('dob_month', models.PositiveIntegerField(blank=True, null=True)),
                ('dob_day', models.PositiveIntegerField(blank=True, null=True)),
                ('first_name', models.CharField(max_length=120, null=True)),
                ('last_name', models.CharField(max_length=120, null=True)),
                ('front_id', models.FileField(storage=arqamhouse.aws.utils.PrivateMediaStorage(), upload_to=houses.models.id_location)),
                ('back_id', models.FileField(storage=arqamhouse.aws.utils.PrivateMediaStorage(), upload_to=houses.models.id_location)),
                ('house', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='houses.House')),
            ],
            options={
                'ordering': ['-created_at', '-updated_at'],
                'abstract': False,
            },
        ),
    ]
