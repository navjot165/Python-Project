from accounts.constants import *
from accounts.models import *
from buses.models import *
import uuid
from django.db import models


class Captain(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="captain_user")
    company = models.ForeignKey('Companies', null=True, blank=True, on_delete=models.CASCADE, related_name="captain_user")
    garage_location = models.TextField(null=True, blank=True)
    garage_lattitude = models.FloatField(null=True, blank=True)
    garage_longitude = models.FloatField(null=True, blank=True)
    sacco_rsl = models.CharField(max_length=255, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_blacklisted = models.BooleanField(default=False, null=True, blank=True)
    mode_of_payment = models.PositiveIntegerField(choices=PAYMENT_MODE, null=True, blank=True)
    plan = models.ForeignKey('Plans', null=True, blank=True, on_delete=models.SET_NULL)
    years_of_experience = models.PositiveIntegerField(null=True, blank=True)
    driving_license_expiry_date = models.DateField(null=True, blank=True, auto_now_add=False)
    driving_license = models.ManyToManyField(Image, related_name="driving_license")
    govt_id_proof = models.ManyToManyField(Image, related_name="govt_id_proof")

    class Meta:
        managed = True
        default_permissions = ();
        db_table = 'captain'
        permissions = [
            ('captains_list','Can View Captains List'),
            ('add_captain','Can Add A Captain'),
            ('edit_captain','Can Edit A Captain Profile'),
            ('view_captain','Can View Captain Details'),
            ('verify_unverify_captain','Can Verify/Unverify Captain Profile'),
            ('activate_deactivate_delete_captain','Can Activate/Deactivate/Delete Captain Profile'),
            ('assign_company','Can Assign Company'),
            ('assign_plan','Can Assign Plan'),
            ('assign_bus','Can Assign Bus'),
        ]



class AssignedCaptainBuses(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    captain = models.ForeignKey(Captain, null=True, blank=True, on_delete=models.CASCADE)
    bus = models.ForeignKey(Buses, null=True, blank=True, on_delete=models.CASCADE)
    assigned_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    assigned_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="assigned_by_user")

    class Meta:
        managed = True
        default_permissions = ();
        db_table = 'assigned_captain_buses'


class Plans(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    plan_type = models.PositiveIntegerField(null=True, blank=True, choices=PLAN_TYPE)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="plan_creator")
    shift_type = models.PositiveIntegerField(null=True, blank=True, choices = SHIFT_TYPE)

    class Meta:
        managed = True
        default_permissions = ();
        db_table = 'plans'
        permissions = [
            ('plans_list','Can View Plans List'),
            ('add_plan','Can Add A Plan'),
            ('edit_plan','Can Edit A Plan'),
            ('delete_plan','Can Delete A Plan'),
            ('view_plan','Can View Plan Details'),
        ]


class Companies(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    company_logo = models.FileField(upload_to='company_logo/', blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    company_type = models.PositiveIntegerField(choices = COMPANY_TYPE, null=True, blank=True)
    payment_mode = models.PositiveIntegerField(choices=COMPANY_PAYMENT_MODE, null=True, blank=True)
    bank_account_number = models.CharField(max_length=255, null=True, blank=True)
    mobile_money_number = models.CharField(max_length=255, null=True, blank=True)
    company_poc = models.ManyToManyField('CompanyPOC')


    class Meta:
        managed = True
        default_permissions = ();
        db_table = 'companies'
        permissions = [
            ('companies_list','Can View Companies List'),
            ('add_company','Can Add A Company'),
            ('edit_company','Can Edit A Company'),
            ('delete_company','Can Delete A Company'),
            ('view_company','Can View Company Details'),
        ]


class CompanyPOC(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(null=True, blank=True, max_length=255)
    country_code = models.CharField(null=True, blank=True, max_length=10)
    mobile_no = models.CharField(null=True, blank=True, max_length=255)
    profile_pic = models.FileField(upload_to='company_poc', null=True, blank=True)

    class Meta:
        managed = True
        default_permissions = ();
        db_table = 'company_poc'