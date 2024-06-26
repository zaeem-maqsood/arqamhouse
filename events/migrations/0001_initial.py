# Generated by Django 2.2.4 on 2019-09-03 15:47

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import events.models.events
import events.models.orders


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('questions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(blank=True, max_length=300, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Attendee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('name', models.CharField(blank=True, max_length=150, null=True)),
                ('email', models.EmailField(blank=True, max_length=120, null=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female')], default='female', max_length=20, null=True)),
                ('age', models.PositiveSmallIntegerField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-created_at', '-updated_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AttendeeCommonQuestions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notes', models.BooleanField(default=False)),
                ('notes_required', models.BooleanField(default=False)),
                ('age', models.BooleanField(default=False)),
                ('age_required', models.BooleanField(default=False)),
                ('gender', models.BooleanField(default=False)),
                ('gender_required', models.BooleanField(default=False)),
                ('country', models.BooleanField(default=False)),
                ('country_required', models.BooleanField(default=False)),
                ('region', models.BooleanField(default=False)),
                ('region_required', models.BooleanField(default=False)),
                ('city', models.BooleanField(default=False)),
                ('city_required', models.BooleanField(default=False)),
                ('email', models.BooleanField(default=False)),
                ('email_required', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Checkin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120, null=True)),
                ('auto_add_new_attendees', models.BooleanField(default=True)),
                ('password_protected', models.BooleanField(default=True)),
                ('password', models.CharField(max_length=120, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('title', models.CharField(max_length=120, null=True)),
                ('url', models.CharField(blank=True, max_length=120, null=True)),
                ('slug', models.SlugField(blank=True, max_length=175)),
                ('start', models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ('end', models.DateTimeField(null=True)),
                ('venue_address', models.CharField(blank=True, max_length=200, null=True)),
                ('venue_name', models.CharField(blank=True, max_length=200, null=True)),
                ('short_description', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to=events.models.events.image_location)),
                ('public', models.BooleanField(default=True)),
                ('active', models.BooleanField(default=True)),
                ('deleted', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-created_at', '-updated_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EventCart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('processed', models.BooleanField(default=False)),
                ('total_no_fee', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('total', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('total_fee', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('arqam_charge', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('stripe_charge', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EventCartItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(blank=True)),
                ('donation_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('free_ticket', models.BooleanField(default=False)),
                ('paid_ticket', models.BooleanField(default=False)),
                ('donation_ticket', models.BooleanField(default=False)),
                ('pass_fee', models.BooleanField(default=False)),
                ('ticket_price', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('cart_item_total_no_fee', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('cart_item_total', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EventEmailConfirmation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EventOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=150, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('email', models.EmailField(max_length=300)),
                ('failed', models.BooleanField(default=False)),
                ('refunded', models.BooleanField(default=False)),
                ('note', models.TextField(blank=True, null=True)),
                ('pdf', models.FileField(blank=True, null=True, upload_to=events.models.orders.pdf_location)),
                ('code', models.ImageField(blank=True, null=True, upload_to=events.models.orders.qrcode_location)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.Event')),
                ('event_cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.EventCart')),
            ],
        ),
        migrations.CreateModel(
            name='EventQuestion',
            fields=[
                ('question', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='questions.Question')),
                ('order_question', models.BooleanField(default=False)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.Event')),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=100, null=True)),
                ('slug', models.SlugField(blank=True, max_length=175)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('buyer_price', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('fee', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('min_amount', models.PositiveSmallIntegerField(blank=True, default=0)),
                ('max_amount', models.PositiveSmallIntegerField(blank=True, default=10)),
                ('description', models.TextField(blank=True, null=True)),
                ('paid', models.BooleanField(default=False)),
                ('pass_fee', models.BooleanField(default=True)),
                ('free', models.BooleanField(default=False)),
                ('donation', models.BooleanField(default=False)),
                ('sold_out', models.BooleanField(default=False)),
                ('amount_available', models.PositiveSmallIntegerField(blank=True, default=3000, null=True)),
                ('amount_sold', models.PositiveSmallIntegerField(blank=True, default=0)),
                ('deleted', models.BooleanField(default=False)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.Event')),
            ],
        ),
        migrations.CreateModel(
            name='OrderAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(blank=True, max_length=300, null=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.EventOrder')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.EventQuestion')),
            ],
        ),
        migrations.AddField(
            model_name='eventquestion',
            name='tickets',
            field=models.ManyToManyField(blank=True, to='events.Ticket'),
        ),
    ]
