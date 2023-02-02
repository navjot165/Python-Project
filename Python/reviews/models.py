import uuid
from django.db import models
from accounts.models import *


class ReviewText(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.TextField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        managed=True
        default_permissions = ()
        db_table = 'review_text'
        permissions = [
            ('review_texts_list','Can View Review Texts List'),
            ('add_review_text','Can Add A Review Text'),
            ('edit_review_text','Can Edit A Review Text'),
            ('delete_review_text','Can Delete A Review Text'),
        ]