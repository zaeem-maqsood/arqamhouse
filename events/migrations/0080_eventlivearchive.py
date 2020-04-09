# Generated by Django 2.2 on 2020-04-07 03:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0079_eventlive_archive_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventLiveArchive',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('archive_id', models.CharField(blank=True, max_length=400, null=True)),
                ('event_live', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.EventLive')),
            ],
        ),
    ]