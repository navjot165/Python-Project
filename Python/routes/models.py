import uuid
from accounts.constants import *
from accounts.models import *
from buses.models import *
from captains.models import *
from holidays.models import *
from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError


class Stations(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    latitude = models.FloatField(null=True,blank=True)
    longitude = models.FloatField(null=True,blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    district = models.ForeignKey(District, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'stations'
        permissions = [
            ('stations_list','Can View Stations List'),
            ('add_station','Can Add A Station'),
            ('view_station','Can View Station Details'),
            ('delete_station','Can Delete A Station'),
        ]

    def __str__(self):
        return str(self.name)


class Routes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    route_name = models.TextField(blank=True,null=True)
    description = models.TextField(blank=True,null=True)
    is_active = models.BooleanField(default=True)
    show = models.BooleanField(default=False, null=True, blank=True)
    start_station = models.ForeignKey(Stations,on_delete=models.CASCADE, null=True, blank=True, related_name="route_start_station")
    end_station = models.ForeignKey(Stations,on_delete=models.CASCADE, null=True, blank=True, related_name="route_end_station")
    city = models.ForeignKey(Cities, null=True, blank=True, on_delete=models.SET_NULL)
    distance = models.FloatField(null=True, blank=True)
    duration = models.TimeField(null=True, blank=True, auto_now_add=False)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    overview_polyline = models.TextField(null=True, blank=True)
    total_time_minutes = models.CharField(max_length=200, null=True, blank=True)   
    total_distance_km = models.CharField(max_length=200, null=True, blank=True)   
    timezone = models.CharField(null=True,blank=True, max_length=255)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'routes'
        permissions = [
            ('routes_list','Can View Routes List'),
            ('add_route','Can Add A Route'),
            ('edit_route','Can Edit A Route'),
            ('view_route','Can View Route Details'),
            ('delete_route','Can Delete A Route'),
            ('activate_deactivate_route','Can Activate/Deactivate Route'),
        ]


class RoutesStations(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    station = models.ForeignKey(Stations,on_delete=models.CASCADE, null=True, blank=True)
    index = models.PositiveIntegerField(default=1, null=True, blank=True)
    route = models.ForeignKey(Routes,on_delete=models.CASCADE, null=True, blank=True)
    time_minutes = models.PositiveIntegerField(null=True, blank=True, default=0)
    distance_km = models.FloatField(null=True, blank=True, default=0)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'route_station'


class RouteStationsCombination(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    from_station = models.ForeignKey(Stations, null=True, blank=True, on_delete=models.CASCADE, related_name='from_station')
    to_station = models.ForeignKey(Stations, null=True, blank=True, on_delete=models.CASCADE, related_name='to_station')
    time_minutes = models.CharField(max_length=200, null=True, blank=True)   
    route = models.ForeignKey(Routes, null=True, blank=True, on_delete=models.CASCADE) 
    distance_km = models.CharField(max_length=200, null=True, blank=True)   
    break_time_minutes = models.PositiveIntegerField(null=True, blank=True,default=0)   
    
    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'station_combination'   


class Schedules(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    start_station = models.ForeignKey(Stations,on_delete=models.CASCADE, null=True, blank=True, related_name="schedule_start_station")
    end_station = models.ForeignKey(Stations,on_delete=models.CASCADE, null=True, blank=True, related_name="schedule_end_station")
    route = models.ForeignKey(Routes, null=True, blank=True, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE)
    arrival_allowance = models.PositiveIntegerField(null=True, blank=True)
    departure_allowance = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    start_time = models.TimeField(auto_now_add=False,null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    schedule_price = models.FloatField(null=True, blank=True)
    sunday = models.BooleanField(default=False, null=True, blank=True)
    monday = models.BooleanField(default=False, null=True, blank=True)
    tuesday = models.BooleanField(default=False, null=True, blank=True)
    wednesday = models.BooleanField(default=False, null=True, blank=True)
    thursday = models.BooleanField(default=False, null=True, blank=True)
    friday = models.BooleanField(default=False, null=True, blank=True)
    saturday = models.BooleanField(default=False, null=True, blank=True)
    price_overrided = models.BooleanField(default=False, null=True, blank=True)
    base_fare = models.FloatField(null=True, blank=True)
    max_fare = models.FloatField(null=True, blank=True)
    base_distance = models.FloatField(null=True, blank=True)
    distance_bucket_size = models.FloatField(null=True, blank=True)
    distance_bucket_fare = models.FloatField(null=True, blank=True)
    time_bucket_size = models.PositiveIntegerField(null=True, blank=True)
    time_bucket_fare = models.PositiveIntegerField(null=True, blank=True)
    timezone = models.CharField(null=True,blank=True, max_length=255)
    assigned_captain = models.ForeignKey(Captain,on_delete=models.SET_NULL,blank=True,null=True)
    assigned_bus = models.ForeignKey(Buses, null=True, blank=True, on_delete=models.SET_NULL)
    max_seats_per_person = models.PositiveIntegerField(null=True, blank=True)
    flags = models.PositiveIntegerField(choices = CATEGORY_FLAGS, null=True, blank=True)
    category_type = models.PositiveIntegerField(choices = CATEGORY_TYPE, null=True, blank=True)
    total_time_minutes = models.CharField(max_length=200, null=True, blank=True)   
    total_distance_km = models.CharField(max_length=200, null=True, blank=True)   
    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'schedule'
        permissions = [
            ('schedules_list','Can View Schedules List'),
            ('add_schedule','Can Add A Schedule'),
            ('edit_schedule','Can Edit A Schedule'),
            ('delete_schedule','Can Delete A Schedule'),
            ('view_schedule','Can View Schedule Details'),
            ('activate_deactivate_schedule','Can Activate/Deactivate A Schedule'),
        ]


class CancelReason(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255,blank=True,null=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    type_id = models.PositiveIntegerField(choices=CANCELLATION_REASONS, null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'cancel_reason'
        permissions = [
            ('cancel_reasons_list','Can View Cancellaton Reasons List'),
            ('add_cancel_reason','Can Add A Cancellaton Reason'),
            ('delete_cancel_reason','Can Delete A Cancellaton Reason'),
            ('activate_deactivate_reason','Can Activate/Deactivate A Cancellaton Reason'),
        ]



class SelectedCancelReason(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reason = models.TextField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'selected_cancel_reason'


class Rides(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    start_datetime = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    end_datetime = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    actual_start_datetime = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    actual_end_datetime = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    dispatch_datetime = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    dispatch_type = models.PositiveIntegerField(null=True, blank=True, choices=DISPATCH_TYPES)
    schedule = models.ForeignKey(Schedules, null=True, blank=True, on_delete=models.CASCADE)
    route = models.ForeignKey(Routes, null=True, blank=True, on_delete=models.CASCADE)
    ride_price = models.FloatField(null=True, blank=True)
    ride_status = models.PositiveIntegerField(choices=RIDE_STATUS, null=True, blank=True, default=SCHEDULED_RIDE)
    assigned_captain = models.ForeignKey(Captain,on_delete=models.SET_NULL,blank=True,null=True, related_name="ride_assigned_captain")
    actual_captain = models.ForeignKey(Captain,on_delete=models.SET_NULL,blank=True,null=True, related_name="actual_captain")
    is_manual = models.BooleanField(default=False)
    is_emergency = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=True)
    flags = models.PositiveIntegerField(choices = CATEGORY_FLAGS, null=True, blank=True)
    category_type = models.PositiveIntegerField(choices = CATEGORY_TYPE, null=True, blank=True)
    start_ride_station = models.ForeignKey(Stations, null=True, blank=True, on_delete=models.CASCADE, related_name='start_ride_station')
    end_ride_station = models.ForeignKey(Stations, null=True, blank=True, on_delete=models.CASCADE, related_name='end_ride_station')
    price_config = models.PositiveIntegerField(choices=PRICE_CONFIG_TYPE, null=True, blank=True)
    bookings_count = models.PositiveIntegerField(default=0, null=True, blank=True)
    is_fully_booked = models.BooleanField(default=False)
    assigned_bus = models.ForeignKey(Buses, null=True, blank=True, on_delete=models.SET_NULL)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    cancelled_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="cancelled_by")
    cancellation_reasons = models.ManyToManyField(SelectedCancelReason)
    cancelled_at = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    affected_bookings = models.PositiveIntegerField(null=True, blank=True, default=0)
    live_tracking = models.BooleanField(default=False)
    gps = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    dead_kms = models.FloatField(null=True, blank=True)
    in_ride_dead_kms = models.FloatField(null=True, blank=True)
    out_ride_dead_kms = models.FloatField(null=True, blank=True)
    to_garage_dead_kms = models.FloatField(null=True, blank=True)
    from_garage_dead_kms = models.FloatField(null=True, blank=True)
    timezone = models.CharField(null=True,blank=True, max_length=255)
    total_seats = models.PositiveIntegerField(null=True, blank=True, default=0)
    seats_left = models.PositiveIntegerField(null=True, blank=True, default=0)
    max_seats_per_person = models.PositiveIntegerField(null=True, blank=True)
    arrival_allowance = models.PositiveIntegerField(null=True, blank=True)
    departure_allowance = models.PositiveIntegerField(null=True, blank=True)

    def clean(self):
        start_datetime_in_range = Q(start_datetime__lte=self.start_datetime, end_datetime__gte=self.start_datetime)
        end_datetime_in_range = Q(start_datetime__lte=self.end_datetime, end_datetime__gte=self.end_datetime)
        queryset = self._meta.default_manager.filter(start_datetime_in_range | end_datetime_in_range, route=self.route, schedule=self.schedule, assigned_bus=self.assigned_bus, ride_status=SCHEDULED_RIDE)
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)
        if queryset.exists():
            raise ValidationError('An existing ride for the same route, schedule and bus clashes with the added one!')

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'rides'
        permissions = [
            ('rides_list','Can View Rides List'),
            ('add_ride','Can Add A Ride'),
            ('edit_ride','Can Edit A Ride'),
            ('delete_ride','Can Delete A Ride'),
            ('view_ride','Can View Ride Details'),
            ('view_ride_passengers','Can View Ride Passengers'),
            ('start_end_ride','Can Start/End A Ride'),
            ('change_booking_status','Can Mark CheckIn/CheckOut/Miss A Ride Passenger Booking'),
            ('cancel_ride','Can Cancel Ride'),
        ]


class RequestedRides(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pickup_latitude = models.FloatField(null=True, blank=True)
    pickup_longitude = models.FloatField(null=True, blank=True)
    pickup_address = models.TextField(null=True, blank=True)
    dropoff_latitude = models.FloatField(null=True, blank=True)
    dropoff_longitude = models.FloatField(null=True, blank=True)
    dropoff_address = models.TextField(null=True, blank=True)
    request_count = models.PositiveIntegerField(default=1, null=True, blank=True)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'requested_rides'


class UserRequestedRide(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    requested_ride = models.ForeignKey(RequestedRides, null=True, blank=True, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    preferred_pickup_time = models.DateTimeField(null=True, blank=True, auto_now_add=False)
    preferred_dropoff_time = models.DateTimeField(null=True, blank=True, auto_now_add=False)
    request_count_same_user = models.PositiveIntegerField(null=True, blank=True, default=1)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'user_requested_ride'


class UserRideSearch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    pickup_latitude = models.FloatField(null=True, blank=True)
    pickup_longitude = models.FloatField(null=True, blank=True)
    pickup_address = models.TextField(null=True, blank=True)
    dropoff_latitude = models.FloatField(null=True, blank=True)
    dropoff_longitude = models.FloatField(null=True, blank=True)
    dropoff_address = models.TextField(null=True, blank=True)
    is_ride_available = models.BooleanField(default=False, null=True, blank=True)
    is_pickup_available = models.BooleanField(default=False, null=True, blank=True)
    is_dropoff_available = models.BooleanField(default=False, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    search_count = models.PositiveIntegerField(null=True, blank=True, default=1)

    class Meta:
        managed = True
        default_permissions = ()
        db_table = 'user_ride_search'
        permissions = [
            ('ride_search_list','Can View Rides Search History List'),
            ('view_ride_search','Can View Ride Search History Details'),
            ('delete_ride_search','Can Delete A Ride Search History'),
            ('clear_ride_search','Can Clear Ride Search History'),
        ]
        
