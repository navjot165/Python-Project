import uuid
from django.db import models
from accounts.models import *
from accounts.constants import *


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(null=True, blank=True, max_length=255)
    description = models.TextField(null=True, blank=True)
    base_fare = models.FloatField(null=True, blank=True)
    max_fare = models.FloatField(null=True, blank=True)
    base_distance = models.FloatField(null=True, blank=True)
    distance_bucket_size = models.FloatField(null=True, blank=True)
    distance_bucket_fare = models.FloatField(null=True, blank=True)
    time_bucket_size = models.PositiveIntegerField(null=True, blank=True)
    time_bucket_fare = models.PositiveIntegerField(null=True, blank=True)
    flags = models.PositiveIntegerField(choices = CATEGORY_FLAGS, null=True, blank=True)
    category_type = models.PositiveIntegerField(choices = CATEGORY_TYPE, null=True, blank=True)
    dead_mileage_thresholds = models.CharField(max_length=255, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="category_creator")
    max_seats_per_person = models.PositiveIntegerField(null=True, blank=True)
    arrival_allowance = models.PositiveIntegerField(null=True, blank=True, default=0)
    departure_allowance = models.PositiveIntegerField(null=True, blank=True, default=0)

    class Meta:
        managed=True
        default_permissions = ()
        db_table = 'category'
        permissions = [
            ('category_list','Can View Categories List'),
            ('add_category','Can Add A Category'),
            ('edit_category','Can Edit A Category'),
            ('delete_category','Can Delete A Category'),
            ('view_category','Can View Category Details'),
        ]


class Holidays(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(null=True, blank=True, max_length=255)
    description = models.TextField(null=True, blank=True)
    holiday_date = models.DateField(auto_now_add=False, auto_now=False, null=True, blank=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        managed=True
        default_permissions = ()
        db_table = 'holidays'
        permissions = [
            ('holidays_list','Can View Holidays List'),
            ('add_holiday','Can Add A Holiday'),
            ('edit_holiday','Can Edit A Holiday'),
            ('delete_holiday','Can Delete A Holiday'),
            ('view_holiday','Can View Holiday Details'),
        ]