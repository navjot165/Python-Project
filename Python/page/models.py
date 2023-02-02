import uuid
from accounts.constants import *
from django.db import models
from django.utils.html import strip_tags
from ckeditor_uploader.fields import RichTextUploadingField
from accounts.models import *


class Pages(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255,blank=True, null=True)
    content = RichTextUploadingField()
    type_id = models.PositiveIntegerField(choices=PAGE_TYPE)
    created_on = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    updated_on = models.DateTimeField(auto_now=True,blank=True, null=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['content'] = strip_tags(instance.content)
        return data

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'static_pages'
        permissions = [
            ('pages_list','Can View Static Pages List'),
            ('add_page','Can Add A Static Page'),
            ('edit_page','Can Edit A Static Page'),
            ('view_page','Can View Static Page Details'),
            ('delete_page','Can Delete A Static Page'),
        ]