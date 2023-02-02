from accounts.constants import *
from accounts.models import *
import uuid
from django.db import models


class BusTypes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    seat_count = models.PositiveIntegerField(null=True, blank=True, default=0)
    max_seat_count = models.PositiveIntegerField(null=True, blank=True, default=0)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'bus_types'
        permissions = [
            ('bus_type_list','Can View Bus Types List'),
            ('add_bus_type','Can Add A Bus Type'),
            ('edit_bus_type','Can Edit A Bus Type'),
            ('delete_bus_type','Can Delete A Bus Type'),
            ('view_bus_type','Can View Bus Type Details'),
        ]


class Buses(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plate_number = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_ac = models.BooleanField(default=False)
    is_sacco = models.BooleanField(default=False)
    is_ev = models.BooleanField(default=False)
    is_blacklisted = models.BooleanField(default=False)
    manufacture_year = models.CharField(null=True, blank=True, max_length=20)
    bus_type = models.ForeignKey(BusTypes, null=True, blank=True, on_delete=models.SET_NULL)
    ownership_document = models.ManyToManyField(Image, related_name="ownership_document")
    vehicle_image = models.ManyToManyField(Image, related_name="vehicle_image")
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    ownership_start_date = models.DateField(auto_now_add=False, null=True, blank=True)
    is_active = models.BooleanField(default = True)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    is_regular = models.BooleanField(null=True, blank=True, default=True)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'buses'
        permissions = [
            ('bus_list','Can View Buses List'),
            ('add_bus','Can Add A Bus'),
            ('edit_bus','Can Edit A Bus'),
            ('delete_bus','Can Delete A Bus'),
            ('view_bus','Can View Bus Details'),
            ('activate_deactivate_bus','Can Activate/Deactivate A Bus'),
        ]
