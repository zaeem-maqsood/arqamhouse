# Generated by Django 2.2.3 on 2019-07-29 18:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MultipleChoiceOption',
            new_name='MultipleChoice',
        ),
    ]
