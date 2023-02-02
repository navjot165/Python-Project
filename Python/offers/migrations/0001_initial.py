# Generated by Django 3.0 on 2023-02-02 16:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OfferCodes',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('code', models.CharField(blank=True, max_length=255, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_on', models.DateTimeField(auto_now=True, null=True)),
                ('expiry_date', models.DateField(blank=True, null=True)),
                ('promo_type', models.PositiveIntegerField(blank=True, choices=[(1, 'Percentage'), (2, 'Absolute')], null=True)),
                ('promo_status', models.PositiveIntegerField(blank=True, choices=[(1, 'Active'), (2, 'Inactive'), (3, 'Expired')], null=True)),
                ('off_percentage', models.PositiveIntegerField(blank=True, null=True)),
                ('offer_type', models.PositiveIntegerField(blank=True, choices=[(1, 'Promo code'), (2, 'Referral Rewards')], null=True)),
                ('max_usage_per_person', models.PositiveIntegerField(blank=True, null=True)),
                ('maximum_price', models.FloatField(blank=True, default=0, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'offers',
                'permissions': [('offers_list', 'Can View Offers List'), ('add_offer', 'Can Add An Offer'), ('edit_offer', 'Can Edit An Offer'), ('delete_offer', 'Can Delete An Offer'), ('view_offer', 'Can View Offer Details'), ('activate_deactivate_offer', 'Can Activate/Deactivate An Offer')],
                'managed': True,
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='UserReferralCodeUsed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('referee_benefit_recieved', models.BooleanField(default=False)),
                ('referrer_benefit_recieved', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('referee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='referee', to=settings.AUTH_USER_MODEL)),
                ('referrer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='referrer', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'refferral_code_used',
                'managed': True,
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='OfferCodeUsed',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('used_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('used_count', models.PositiveIntegerField(blank=True, null=True)),
                ('code', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='offers.OfferCodes')),
                ('user', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'offer_used',
                'managed': True,
                'default_permissions': (),
            },
        ),
    ]
