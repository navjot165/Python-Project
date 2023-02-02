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
            name='ContactUs',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('full_name', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.CharField(blank=True, max_length=255, null=True)),
                ('mobile_no', models.CharField(blank=True, max_length=255, null=True)),
                ('message', models.TextField(blank=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'contactus',
                'permissions': [('contact_us_list', 'Can View Contact Us List'), ('delete_contact_us', 'Can Delete A Contact Us'), ('view_contact_us', 'Can View Contact Us Details'), ('reply_contact_us', 'Can Reply To Contact Us')],
                'managed': True,
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ContactUsReply',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('reply_message', models.TextField(blank=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contact_us.ContactUs')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replied_to', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'contactus_reply',
                'managed': True,
                'default_permissions': (),
            },
        ),
    ]
