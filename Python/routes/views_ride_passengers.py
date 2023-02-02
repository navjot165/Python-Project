import environ
import logging
from accounts.decorators import *
from accounts.helper import *
from accounts.utils import *
from captains.models import *
from .models import *
from frontend.views import *
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import render, redirect
from datetime import datetime
env = environ.Env()
environ.Env.read_env()
db_logger = logging.getLogger('db')


@admins_only
@check_permissions('routes.view_ride_passengers')
def RidePassengersList(request, id):
    ride = Rides.objects.get(id=id)
    station_data, bookings_data, passengers_pickedup, passengers_dropedoff = [], [], [], []
    route_stations = RoutesStations.objects.filter(route=ride.route).order_by('index')
    for station in route_stations:
        station_data.append(station.station)
        bookings_data.append(Booking.objects.filter(Q(pickup_station=station.station, is_pickup=False)|Q(dropoff_station=station.station, is_pickup=True),ride=ride))
        passengers_pickedup.append(Booking.objects.filter(Q(status=BOOKED)|Q(status=COMPLETE_BOOKING),pickup_station=station.station,is_pickup=True,ride=ride).count())
        passengers_dropedoff.append(Booking.objects.filter(Q(status=BOOKED)|Q(status=COMPLETE_BOOKING),ride=ride, dropoff_station=station.station,is_dropoff=True).count())
    passengers_data = zip(station_data, bookings_data, passengers_pickedup, passengers_dropedoff)
    return render(request,'rides/ride-passengers.html',{
        "head_title":"Rides Management",
        "ride":ride,
        "boarded_passengers":sum([int(booking.seats_booked if booking.seats_booked else 0) for booking in Booking.objects.filter(ride=ride,is_dropoff=True,status=COMPLETE_BOOKING)]),
        "missed_passengers":sum([int(booking.seats_booked if booking.seats_booked else 0) for booking in Booking.objects.filter(ride=ride, status=MISSED_BOOKING)]),
        "cash_collected":round(sum([float(booking.booking_price if booking.booking_price else 0) for booking in Booking.objects.filter(ride=ride,is_dropoff=True,status=COMPLETE_BOOKING)])),
        "total_seats":sum([int(booking.seats_booked) for booking in Booking.objects.filter(ride=ride).exclude(Q(status=CANCELLED_BOOKING)|Q(status=MISSED_BOOKING))]),
        "passengers_data":passengers_data
    })


@admins_only
@check_permissions('routes.start_end_ride')
def StartRideView(request, id):
    ride = Rides.objects.get(id=id)
    if not Booking.objects.filter(ride=ride):
        messages.error(request, "No Bookings Found On The Ride")
    else:
        ride.ride_status = INPROGRESS_RIDE
        ride.actual_start_datetime = datetime.now()
        ride.save()
        messages.success(request, "Ride Started Successfully!")
    return redirect('routes:ride_passengers',id=id)


@admins_only
@check_permissions('routes.start_end_ride')
def EndRideView(request, id):
    ride = Rides.objects.get(id=id)
    if  Booking.objects.filter(ride=ride,status=BOOKED):
        messages.error(request, "You can not end the ride as all passengers have not either picked/dropped or missed yet.")
    else:
        ride.ride_status = COMPLETED_RIDE
        ride.actual_end_datetime = datetime.now()
        ride.save()
        messages.success(request, "Ride Completed Successfully!")
    return redirect('routes:ride_passengers',id=id)


@admins_only
@check_permissions('routes.change_booking_status')
def ChangeRidePassengersStatus(request, ride_id, booking_id):
    ride = Rides.objects.get(id=ride_id)
    if ride.ride_status == INPROGRESS_RIDE:
        booking = Booking.objects.get(id=booking_id)
        if request.GET.get('check_in'):
            booking.is_pickup = True
            booking.actual_pickup_time = datetime.now()
            message = 'Passenger Checked In Successfully!'
        elif request.GET.get('check_out'):
            booking.is_dropoff = True
            booking.status = COMPLETE_BOOKING
            booking.actual_dropoff_time = datetime.now()
            message = 'Passenger Checked Out Successfully!'
        else:
            booking.status = MISSED_BOOKING
            message = "Passenger Missed!"
        booking.save()
        messages.success(request, message)
    else:
        messages.error(request, 'You need to start the ride first in order to perform actions.')
    return redirect('routes:ride_passengers',id=ride_id)
