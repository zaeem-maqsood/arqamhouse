# Generated by Django 2.2.7 on 2019-12-02 17:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('houses', '0013_house_email'),
        ('events', '0044_requestarefund'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RequestARefund',
            new_name='EventRequestARefund',
        ),
    ]