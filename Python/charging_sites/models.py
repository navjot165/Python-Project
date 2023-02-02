from django.db import models
from accounts.models import *


class ChargingSites(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(null=True, blank=True)
    charging_points_count = models.PositiveIntegerField(null=True, blank=True, default=0)
    capacity = models.PositiveIntegerField(null=True, blank=True, default=0)
    location = models.TextField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    opening_time = models.TimeField(auto_now_add=False, null=True, blank=True)
    closing_time = models.TimeField(auto_now_add=False, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'charging_sites'
        permissions = [
            ('charging_sites_list','Can View Charging Sites List'),
            ('add_charging_site','Can Add A Charging Site'),
            ('edit_charging_site','Can Edit A Charging Site'),
            ('delete_charging_site','Can Delete A Charging Site'),
            ('view_charging_site','Can View Charging Site Details'),
        ]