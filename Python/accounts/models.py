from .constants import *
import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
import os
from django.http import HttpResponse
from django.utils.encoding import smart_str


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=255,blank=True, null=True, unique=True)
    first_name = models.CharField(max_length=255,null=True,blank=True)
    last_name = models.CharField(max_length=255,null=True,blank=True)
    full_name = models.CharField(max_length=255,null=True,blank=True)
    email = models.EmailField("email address", null=True, blank=True)
    mobile_no = models.CharField(max_length=20, null=True, blank=True)
    country_code = models.CharField(max_length=5, null=True, blank=True)
    profile_pic = models.FileField(upload_to='profile_pic/', blank=True, null=True)
    role_id = models.PositiveIntegerField(default=ADMIN,choices=USER_ROLE,null=True, blank=True)
    status = models.PositiveIntegerField(default=ACTIVE, choices=USER_STATUS,null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True,null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    short_location = models.TextField(null=True, blank=True)
    temp_otp = models.CharField(null=True, blank=True, max_length=10)
    otp_verified = models.BooleanField(null=True, blank=True, default=False)
    gender = models.PositiveIntegerField(choices=GENDER, null=True, blank=True)
    send_notifications = models.BooleanField(default=True)
    referral_code = models.CharField(max_length=15, null=True, blank=True)
    is_referred = models.BooleanField(default=False)
    referred_by = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL)
    category = models.PositiveIntegerField(choices = USER_CATEGORY, null=True, blank=True)
    is_profile_setup = models.BooleanField(default=False)
    social_id = models.CharField(max_length=255, null=True, blank=True)
    social_type = models.PositiveIntegerField(choices=SOCIAL_TYPE, null=True, blank=True)
    average_rating = models.FloatField(null=True, blank=True, default=0)
    is_profile_verified = models.BooleanField(default=False, null=True, blank=True)
    city = models.ForeignKey('Cities', null=True, blank=True, on_delete=models.SET_NULL)
    mpesa_number = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'user'
        permissions = [
            ('customers_list','Can View Customers List'),
            ('edit_customer','Can Edit A Customer Profile'),
            ('view_customer','Can View Customer Details'),
            ('activate_deactivate_delete_customer','Can Activate/Deactivate/Delete Customer Profile'),
        ]

    def __str__(self):
        return str(self.username)


class Device(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('User',null=True,blank=True,on_delete=models.CASCADE)
    device_type = models.PositiveIntegerField(choices=DEVICE_TYPE,null=True,blank=True)
    device_name = models.CharField(max_length=255,null=True,blank=True)
    device_token = models.TextField(null=True,blank=True)
    ip_address = models.CharField(max_length=255,null=True,blank=True)
    device_model = models.CharField(max_length=255,null=True,blank=True)
    imei = models.CharField(max_length=255,null=True,blank=True)
    signups_count = models.PositiveIntegerField(default=0, null=True, blank=True)
    bookings_count = models.PositiveIntegerField(default=0, null=True, blank=True)
    
    
    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'device'

    def __str__(self):
        return str(self.device_name)


class LoginHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    User_Ip = models.CharField( max_length=255, null=True, blank=True)
    User_agent = models.CharField(max_length=255, null=True, blank=True)
    State = models.CharField(default=timezone.now, max_length=255, null=True, blank=True)
    Code = models.CharField(default=timezone.now, max_length=255, null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    user = models.CharField( max_length=255, null=True, blank=True)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'login_history'
        permissions = [
            ('loginhistory_list','Can View Login History List'),
            ('clear_loginhistory','Can Clear All Login History'),
        ]


class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_on = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    upload = models.FileField(upload_to='vehicles/', blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL,blank=True,null=True)

    def extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension

    @classmethod
    def Downloadfile(zips,path,upload):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path= os.path.join(BASE_DIR)
        
        file_path = f"media/{upload}"
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(),content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(upload)
            response['X-Sendfile'] = smart_str(path)
        return response

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'image'


class UserWallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.FloatField(null=True, blank=True, default=0)
    user = models.ForeignKey('User',on_delete=models.CASCADE,null=True,blank=True,default=None)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    mpesa_number = models.CharField(max_length=100, null=True, blank=True)
    linked_to_mpesa = models.BooleanField(default=False, null=True, blank=True)
    cards_linked = models.BooleanField(default=False, null=True, blank=True)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'wallet'


class PaymentCycles(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(null=True, blank=True, max_length=255)
    description = models.TextField(null=True, blank=True)
    period = models.PositiveIntegerField(null=True, blank=True)
    start_date = models.DateField(auto_now_add=False, null=True, blank=True)
    end_date = models.DateField(auto_now_add=False, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'payment_cycles'


class Currencies(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=255, null=True, blank=True)
    symbol = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'currencies'
        permissions = [
            ('currencies_list','Can View Currencies List'),
            ('delete_currency','Can Delete A Currency'),
        ]


class Countries(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(null=True, blank=True,max_length=255)
    initials = models.CharField(null=True, blank=True,max_length=10)
    region = models.CharField(null=True, blank=True,max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    currency = models.ForeignKey(Currencies, null=True, blank=True, on_delete=models.SET_NULL)
    default = models.BooleanField(default=False)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'countries'
        permissions = [
            ('countries_list','Can View Countries List'),
            ('add_country','Can Add A Country'),
            ('edit_country','Can Edit A Country'),
            ('delete_country','Can Delete A Country'),
            ('view_country','Can View Country Details'),
        ]


class Cities(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(null=True, blank=True,max_length=255)
    initials = models.CharField(null=True, blank=True,max_length=10)
    country = models.ForeignKey(Countries,null=True, blank=True, on_delete=models.CASCADE)
    status = models.PositiveIntegerField(choices=CITY_STATE, null=True, blank=True, default=ACTIVE_CITY)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    default = models.BooleanField(default=False)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'cities'
        permissions = [
            ('cities_list','Can View Cities List'),
            ('add_city','Can Add A City'),
            ('edit_city','Can Edit A City'),
            ('delete_city','Can Delete A City'),
            ('view_city','Can View City Details'),
        ]


class District(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(null=True, blank=True,max_length=255)
    initials = models.CharField(null=True, blank=True,max_length=10)
    city = models.ForeignKey(Cities,null=True, blank=True, on_delete=models.CASCADE)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'district'
        permissions = [
            ('districts_list','Can View Districts List'),
            ('add_district','Can Add A District'),
            ('edit_district','Can Edit A District'),
            ('delete_district','Can Delete A District'),
            ('view_district','Can View District Details'),
        ]