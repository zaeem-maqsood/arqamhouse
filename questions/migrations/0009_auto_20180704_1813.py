# Generated by Django 2.0.3 on 2018-07-04 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0008_auto_20180704_1650'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventquestionmultiplechoiceoption',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='question',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
    ]
