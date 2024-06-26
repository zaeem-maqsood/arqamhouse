# Generated by Django 2.2.7 on 2019-12-04 17:24

from django.db import migrations, models
import payments.models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0022_banktransfer_official_document'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banktransfer',
            name='official_document',
            field=models.FileField(blank=True, null=True, upload_to=payments.models.official_document_location, validators=[payments.models.validate_file_extension]),
        ),
    ]
