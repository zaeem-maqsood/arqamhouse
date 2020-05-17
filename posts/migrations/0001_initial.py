# Generated by Django 2.2 on 2020-05-17 07:14

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('houses', '0034_remove_house_campaign_view_score'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(blank=True, max_length=150, null=True)),
                ('slug', models.SlugField(blank=True, max_length=175)),
                ('content', models.TextField(blank=True, null=True)),
                ('house', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='houses.House')),
            ],
            options={
                'ordering': ['-created_at', '-updated_at'],
                'abstract': False,
            },
        ),
    ]
