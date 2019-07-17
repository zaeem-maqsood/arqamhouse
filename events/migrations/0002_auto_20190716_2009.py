# Generated by Django 2.2.3 on 2019-07-16 20:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('houses', '0001_initial'),
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='house',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='houses.House'),
        ),
        migrations.AddField(
            model_name='checkin',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.Event'),
        ),
        migrations.AddField(
            model_name='attendeegeneralquestions',
            name='event',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='events.Event'),
        ),
    ]
