import uuid
from accounts.constants import *
from accounts.models import *
from routes.models import *
from captains.models import *
from django.db import models
from offers.models import *


class Booking(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    boarding_pass = models.PositiveIntegerField(null=True, blank=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    route = models.ForeignKey(Routes, null=True, blank=True, on_delete=models.CASCADE)
    status = models.PositiveIntegerField(choices=BOOKING_STATUS,null=True, blank=True)
    seats_booked = models.CharField(max_length=10,blank=True,null=True)
    ride = models.ForeignKey(Rides, null=True, blank=True, on_delete=models.CASCADE)
    actual_pickup_station = models.CharField(null=True, blank=True, max_length=255)
    actual_pickup_lattitude = models.FloatField(null=True, blank=True)
    actual_pickup_longitude = models.FloatField(null=True, blank=True)
    actual_dropoff_station = models.CharField(null=True, blank=True, max_length=255)
    actual_dropoff_lattitude = models.FloatField(null=True, blank=True)
    actual_dropoff_longitude = models.FloatField(null=True, blank=True)
    booking_price = models.FloatField(null=True, blank=True)
    actual_booking_price = models.FloatField(null=True, blank=True)
    payment_method = models.PositiveIntegerField(BOOKING_PAYMENT_METHOD, null=True, blank=True)
    pickup_station = models.ForeignKey(Stations, null=True, blank=True, on_delete=models.CASCADE, related_name='pickup_station')
    dropoff_station = models.ForeignKey(Stations, null=True, blank=True, on_delete=models.CASCADE, related_name='dropoff_station')
    promo_used = models.ForeignKey(OfferCodes, null=True, blank=True, on_delete=models.SET_NULL)
    refund_type = models.PositiveIntegerField(choices=REFUND_TYPE, null=True, blank=True)
    refund_amount = models.FloatField(null=True, blank=True)
    wallet_amount = models.FloatField(null=True, blank=True)
    cash_to_be_paid = models.FloatField(null=True, blank=True)
    actual_cash_paid = models.FloatField(null=True, blank=True)
    estimated_pickup_time = models.DateTimeField(null=True, blank=True, auto_now_add=False)
    estimated_dropoff_time = models.DateTimeField(null=True, blank=True, auto_now_add=False)
    estimated_walking_distance = models.FloatField(null=True, blank=True)
    actual_pickup_time = models.DateTimeField(null=True, blank=True, auto_now_add=False)
    actual_dropoff_time = models.DateTimeField(null=True, blank=True, auto_now_add=False)
    walking_distance_mode = models.PositiveIntegerField(choices = WALKING_DISTANCE_MODE, null=True, blank=True)
    pickup_walking_distance = models.FloatField(null=True, blank=True)
    pickup_walking_time = models.TimeField(auto_now_add=False, null=True, blank=True)
    dropoff_walking_distance = models.FloatField(null=True, blank=True)
    dropoff_walking_time = models.TimeField(auto_now_add=False, null=True, blank=True)
    check_in_time = models.DateTimeField(null=True, blank=True, auto_now_add=False)
    check_out_time = models.DateTimeField(null=True, blank=True, auto_now_add=False)
    cancelled_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="booking_cancelled_by")
    cancellation_reason = models.ForeignKey(CancelReason, null=True, blank=True, on_delete=models.SET_NULL)
    custom_cancellation_reason = models.TextField(null=True, blank=True)
    cancelled_at = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    overview_polyline = models.TextField(null=True, blank=True)
    is_pickup = models.BooleanField(default=False)
    is_dropoff = models.BooleanField(default=False)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'booking'
        permissions = [
            ('bookings_list','Can View Bookings List'),
            ('view_booking','Can View Booking Details'),
        ]


class Reviews(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.TextField(null=True, blank=True)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'reviews'


class Rating(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rating = models.CharField(null=True, blank=True, max_length=100)
    reviews = models.ManyToManyField(Reviews)
    message = models.TextField(null=True, blank=True)
    created_for = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='rated')
    booking = models.ForeignKey(Booking, null=True, blank=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="rating_by")
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'rating'


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=500, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    notification_type = models.PositiveIntegerField(choices=NOTIFICATION_TYPE,null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications", null=True, blank=True)
    created_for = models.ForeignKey(User, on_delete=models.CASCADE, related_name="_notifications", null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    booking = models.ForeignKey(Booking, null=True, blank=True, on_delete=models.CASCADE)
    captain = models.ForeignKey(Captain, null=True, blank=True, on_delete=models.CASCADE)
    ride = models.ForeignKey(Rides, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'notification'
        verbose_name_plural = "notification"

    def __str__(self):
        return self.title



class Transactions(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_id = models.CharField(null=True, blank=True, max_length=20)
    created_by = models.ForeignKey(User, related_name='transaction_by', on_delete=models.CASCADE, null=True, blank=True)
    created_for = models.ForeignKey(User, related_name='transaction_for', on_delete=models.CASCADE, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    amount = models.CharField(null=True, blank=True, max_length=255)
    currency = models.ForeignKey(Currencies, null=True, blank=True, on_delete=models.SET_NULL)
    booking = models.ForeignKey(Booking, null=True, blank=True, on_delete=models.CASCADE)
    transaction_type = models.PositiveIntegerField(choices=TRANSACTION_TYPE, null=True, blank=True, default=AMOUNT_RECIEVED)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'transactions'


class Tickets(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_number = models.CharField(max_length=100,blank=True,null=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    booking = models.ForeignKey(Booking,on_delete=models.CASCADE,blank=True,null=True)
    ride = models.ForeignKey(Rides, null=True, blank=True, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True,blank=True,null=True)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'ticket'