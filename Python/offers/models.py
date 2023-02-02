import uuid
from django.db import models
from accounts.models import *
from routes.models import *
from accounts.constants import *


class OfferCodes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    code = models.CharField(max_length=255, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    expiry_date = models.DateField(auto_now_add=False, null=True, blank=True)
    promo_type = models.PositiveIntegerField(null=True, blank=True, choices = PROMO_TYPE)
    promo_status = models.PositiveIntegerField(choices = PROMO_STATUS, null=True, blank=True)
    off_percentage = models.PositiveIntegerField(null=True, blank=True)
    routes = models.ManyToManyField(Routes)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    offer_type = models.PositiveIntegerField(null=True, blank=True, choices=OFFER_TYPES)
    max_usage_per_person = models.PositiveIntegerField(null=True, blank=True)
    maximum_price = models.FloatField(null=True, blank=True, default=0)

    class Meta:
        managed=True
        default_permissions = ()
        db_table = 'offers'
        permissions = [
            ('offers_list','Can View Offers List'),
            ('add_offer','Can Add An Offer'),
            ('edit_offer','Can Edit An Offer'),
            ('delete_offer','Can Delete An Offer'),
            ('view_offer','Can View Offer Details'),
            ('activate_deactivate_offer','Can Activate/Deactivate An Offer'),
        ]


class OfferCodeUsed(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE,default=None)
    code = models.ForeignKey(OfferCodes, null=True, blank=True, on_delete=models.CASCADE,default=None)
    used_on = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    used_count = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        managed=True
        default_permissions = ()
        db_table = 'offer_used'


class UserReferralCodeUsed(models.Model):
    referee = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='referee')
    referrer = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='referrer')
    referee_benefit_recieved = models.BooleanField(default=False)
    referrer_benefit_recieved = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True,null=True, blank=True)

    class Meta:
        managed = True
        default_permissions = ();
        db_table = 'refferral_code_used'