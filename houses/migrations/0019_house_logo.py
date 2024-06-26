# Generated by Django 2.2 on 2020-01-17 15:51

from django.db import migrations, models
import houses.models


class Migration(migrations.Migration):

    dependencies = [
        ('houses', '0018_auto_20200109_1149'),
    ]

    operations = [
        migrations.AddField(
            model_name='house',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to=houses.models.image_location, validators=[houses.models.validate_file_size]),
        ),
    ]
