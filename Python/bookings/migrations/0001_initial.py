# Generated by Django 3.0 on 2023-02-02 16:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('boarding_pass', models.PositiveIntegerField(blank=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_on', models.DateTimeField(auto_now=True, null=True)),
                ('status', models.PositiveIntegerField(blank=True, choices=[(1, 'BOOKED'), (2, 'COMPLETE'), (3, 'CANCELLED'), (4, 'MISSED')], null=True)),
                ('seats_booked', models.CharField(blank=True, max_length=10, null=True)),
                ('actual_pickup_station', models.CharField(blank=True, max_length=255, null=True)),
                ('actual_pickup_lattitude', models.FloatField(blank=True, null=True)),
                ('actual_pickup_longitude', models.FloatField(blank=True, null=True)),
                ('actual_dropoff_station', models.CharField(blank=True, max_length=255, null=True)),
                ('actual_dropoff_lattitude', models.FloatField(blank=True, null=True)),
                ('actual_dropoff_longitude', models.FloatField(blank=True, null=True)),
                ('booking_price', models.FloatField(blank=True, null=True)),
                ('actual_booking_price', models.FloatField(blank=True, null=True)),
                ('payment_method', models.PositiveIntegerField(blank=True, null=True, verbose_name=((1, 'MPesa'), (2, 'Wallet')))),
                ('refund_type', models.PositiveIntegerField(blank=True, choices=[(1, 'Full_Refund'), (2, 'Partial_Refund')], null=True)),
                ('refund_amount', models.FloatField(blank=True, null=True)),
                ('wallet_amount', models.FloatField(blank=True, null=True)),
                ('cash_to_be_paid', models.FloatField(blank=True, null=True)),
                ('actual_cash_paid', models.FloatField(blank=True, null=True)),
                ('estimated_pickup_time', models.DateTimeField(blank=True, null=True)),
                ('estimated_dropoff_time', models.DateTimeField(blank=True, null=True)),
                ('estimated_walking_distance', models.FloatField(blank=True, null=True)),
                ('actual_pickup_time', models.DateTimeField(blank=True, null=True)),
                ('actual_dropoff_time', models.DateTimeField(blank=True, null=True)),
                ('walking_distance_mode', models.PositiveIntegerField(blank=True, choices=[(1, 'Walking'), (2, 'Driving')], null=True)),
                ('pickup_walking_distance', models.FloatField(blank=True, null=True)),
                ('pickup_walking_time', models.TimeField(blank=True, null=True)),
                ('dropoff_walking_distance', models.FloatField(blank=True, null=True)),
                ('dropoff_walking_time', models.TimeField(blank=True, null=True)),
                ('check_in_time', models.DateTimeField(blank=True, null=True)),
                ('check_out_time', models.DateTimeField(blank=True, null=True)),
                ('custom_cancellation_reason', models.TextField(blank=True, null=True)),
                ('cancelled_at', models.DateTimeField(blank=True, null=True)),
                ('overview_polyline', models.TextField(blank=True, null=True)),
                ('is_pickup', models.BooleanField(default=False)),
                ('is_dropoff', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'booking',
                'permissions': [('bookings_list', 'Can View Bookings List'), ('view_booking', 'Can View Booking Details')],
                'managed': True,
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(blank=True, max_length=500, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_read', models.BooleanField(default=False)),
                ('notification_type', models.PositiveIntegerField(blank=True, choices=[(1, 'Booking'), (2, 'Schedule'), (3, 'Rating')], null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'notification',
                'db_table': 'notification',
                'managed': True,
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('rating', models.CharField(blank=True, max_length=100, null=True)),
                ('message', models.TextField(blank=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_on', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'db_table': 'rating',
                'managed': True,
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='Reviews',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('review', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'reviews',
                'managed': True,
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='Transactions',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('transaction_id', models.CharField(blank=True, max_length=20, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('amount', models.CharField(blank=True, max_length=255, null=True)),
                ('transaction_type', models.PositiveIntegerField(blank=True, choices=[(1, 'Amount_Recieved'), (2, 'Amount_Deducted')], default=1, null=True)),
                ('booking', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bookings.Booking')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transaction_by', to=settings.AUTH_USER_MODEL)),
                ('created_for', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transaction_for', to=settings.AUTH_USER_MODEL)),
                ('currency', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.Currencies')),
            ],
            options={
                'db_table': 'transactions',
                'managed': True,
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='Tickets',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('ticket_number', models.CharField(blank=True, max_length=100, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('booking', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bookings.Booking')),
            ],
            options={
                'db_table': 'ticket',
                'managed': True,
                'default_permissions': (),
            },
        ),
    ]