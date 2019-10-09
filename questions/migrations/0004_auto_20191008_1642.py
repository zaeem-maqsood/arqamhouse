# Generated by Django 2.2.5 on 2019-10-08 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0003_multiplechoice_deleted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='question_type',
            field=models.CharField(choices=[('Simple', 'Simple'), ('Long', 'Long'), ('Multiple Choice', 'Multiple Choice')], default='Simple', max_length=50),
        ),
    ]
