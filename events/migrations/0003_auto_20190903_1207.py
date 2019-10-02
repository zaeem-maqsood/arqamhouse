# Generated by Django 2.2.4 on 2019-09-03 16:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_auto_20190903_1147'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendee',
            name='cart_item',
        ),
        migrations.AddField(
            model_name='attendee',
            name='ticket',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='events.Ticket'),
            preserve_default=False,
        ),
    ]