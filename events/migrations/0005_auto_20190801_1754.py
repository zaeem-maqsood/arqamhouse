# Generated by Django 2.2.4 on 2019-08-01 17:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cities_light', '0008_city_timezone'),
        ('events', '0004_auto_20190731_1648'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='attendee',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='events.Attendee'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='attendee',
            name='age',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='attendee',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cities_light.City'),
        ),
        migrations.AddField(
            model_name='attendee',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cities_light.Country'),
        ),
        migrations.AddField(
            model_name='attendee',
            name='note',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='attendee',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cities_light.Region'),
        ),
        migrations.AlterField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.EventQuestion'),
        ),
        migrations.CreateModel(
            name='OrderAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(blank=True, max_length=300, null=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.EventOrder')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.EventQuestion')),
            ],
        ),
    ]
