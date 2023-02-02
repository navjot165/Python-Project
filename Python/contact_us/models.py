from django.db import models
from accounts.models import *
import uuid


class ContactUs(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    mobile_no = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        default_permissions = ();
        db_table = 'contactus'
        permissions = [
            ('contact_us_list','Can View Contact Us List'),
            ('delete_contact_us','Can Delete A Contact Us'),
            ('view_contact_us','Can View Contact Us Details'),
            ('reply_contact_us','Can Reply To Contact Us'),
        ]


class ContactUsReply(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact = models.ForeignKey('ContactUs',null=True,blank=True,on_delete=models.CASCADE)
    reply_message = models.TextField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="replied_to")

    class Meta:
        managed = True
        default_permissions = ();
        db_table = 'contactus_reply'