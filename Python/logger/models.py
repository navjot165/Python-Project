from django.db import models
from accounts.models import *
import uuid


class EmailLogger(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reciever = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    email_template = models.TextField(null=True, blank=True)
    recievers_email = models.CharField(null=True, blank=True, max_length=100)
    sender_email = models.CharField(null=True, blank=True, max_length=100)
    sent_status = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'email_logger'
        permissions = [
            ('email_logs_list','Can View Email Logs List'),
            ('view_email_log','Can View An Email Log Details'),
            ('delete_email_log','Can Delete An Email Log'),
            ('clear_email_logs','Can Clear All Email Logs'),
        ]


class ApplicationCrashLogs(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    error = models.TextField(null=True, blank=True)
    link = models.TextField(null=True, blank=True)
    referer_link = models.TextField(null=True, blank=True)
    user_ip = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_on = models.DateTimeField(null=True, blank=True, auto_now_add=True)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'application_crash_logs'
        permissions = [
            ('application_crashes_list','Can View Application Error Logs List'),
            ('view_application_crash','Can View An Application Error Log Details'),
            ('delete_application_crash','Can Delete An Application Error Log'),
            ('clear_application_crashes','Can Clear All Application Error Logs'),
        ]