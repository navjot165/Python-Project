from django.db import models
import uuid
from accounts.models import *
from accounts.constants import *
from holidays.models import *
from cities.models import *
from routes.models import *


class Dispatcher(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    no_of_days = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=False, null=True, blank=True)
    allow_manual_dispatch = models.BooleanField(default=True, null=True, blank=True)
    categories = models.ManyToManyField(Category)
    cities = models.ManyToManyField(Cities)
    run_current_day = models.BooleanField(default=False, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    total_runs = models.PositiveIntegerField(null=True, blank=True,default=0)

    class Meta:
        managed=True
        default_permissions = ()
        db_table = 'dispatcher'
        permissions = [
            ('dispatcher_list','Can View Offers List'),
            ('add_dispatch','Can Add A Dispatch'),
            ('edit_dispatch','Can Edit A Dispatch'),
            ('delete_dispatch','Can Delete A Dispatch'),
            ('view_dispatch','Can View Dispatch Details'),
            ('activate_deactivate_dispatch','Can Activate/Deactivate A Dispatch'),
            ('dispatch_manual_rides','Can Dispatch Manual Rides'),
        ]


class DispatcherReports(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dispatcher = models.ForeignKey(Dispatcher, null=True, blank=True, on_delete=models.CASCADE)
    dispatched_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    rides_dispatched = models.PositiveIntegerField(null=True, blank=True, default=0)
    status = models.PositiveIntegerField(choices=DISPATCHER_STATUS, null=True, blank=True)
    rides = models.ManyToManyField(Rides)
    dispatch_type = models.PositiveIntegerField(choices = DISPATCH_TYPES, null=True, blank=True)

    class Meta:
        managed=True
        default_permissions = ()
        db_table = 'dispatcher_reports'