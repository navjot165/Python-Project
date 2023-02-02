import environ
import logging
from accounts.decorators import *
from accounts.helper import getLatLongList
from accounts.utils import *
from .models import *
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import render, redirect
from captains.models import *

env = environ.Env()
environ.Env.read_env()
db_logger = logging.getLogger('db')


@admins_only
@check_permissions('bookings.bookings_list')
def BookingsList(request):
    bookings = Booking.objects.all().order_by('-created_on')
    if request.GET.get('boarding_pass'):
        bookings = bookings.filter(boarding_pass__icontains = request.GET.get('boarding_pass'))
    if request.GET.get('pickup_station'):
        bookings = bookings.filter(pickup_station__address__icontains = request.GET.get('pickup_station'))
    if request.GET.get('dropoff_station'):
        bookings = bookings.filter(dropoff_station__address__icontains = request.GET.get('dropoff_station'))
    if request.GET.get('estimated_pickup_time'):
        bookings = bookings.filter(estimated_pickup_time__date = request.GET.get('estimated_pickup_time'))
    if request.GET.get('created_by'):
        bookings = bookings.filter(Q(booking__created_by__full_name__icontains=request.GET.get('created_by')|Q(booking__created_by__mobile_no__icontains=request.GET.get('created_by'))))
    if request.GET.get('seats_booked'):
        bookings = bookings.filter(seats_booked=request.GET.get('seats_booked'))
    if request.GET.get('booking_price'):
        bookings = bookings.filter(booking_price__icontains=request.GET.get('booking_price'))
    if request.GET.get('status'):
        bookings = bookings.filter(status=request.GET.get('status'))
    if request.GET and not bookings:
        messages.error(request, 'No Data Found')
        
    return render(request, 'bookings/bookings-list.html',{
        "head_title":"Bookings Management",
        "bookings":get_pagination(request, bookings),
        "boarding_pass":request.GET.get('boarding_pass') if request.GET.get('boarding_pass') else "",
        "pickup_station":request.GET.get('pickup_station') if request.GET.get('pickup_station') else "",
        "dropoff_station":request.GET.get('dropoff_station') if request.GET.get('dropoff_station') else "",
        "estimated_pickup_time":request.GET.get('estimated_pickup_time') if request.GET.get('estimated_pickup_time') else "",
        "created_by":request.GET.get('created_by') if request.GET.get('created_by') else "",
        "seats_booked":request.GET.get('seats_booked') if request.GET.get('seats_booked') else "",
        "booking_price":request.GET.get('booking_price') if request.GET.get('booking_price') else "",
        "status":request.GET.get('status') if request.GET.get('status') else "",
    })


@admins_only
@check_permissions('bookings.view_booking')
def ViewBooking(request, id):
    booking = Booking.objects.get(id=id)
    first_station = RoutesStations.objects.filter(route = booking.route, station=booking.pickup_station).order_by("index").first()
    last_station = RoutesStations.objects.filter(route = booking.route, station=booking.dropoff_station).order_by("index").last()
    inbetween_stations = []
    for station_index in range(int(first_station.index)+1,int(last_station.index)):
        inbetween_station = RoutesStations.objects.get(index = station_index,route = booking.route)
        inbetween_stations.append(str(inbetween_station.station.latitude) + "," + str(inbetween_station.station.longitude))
    polyline_coordinates = getLatLongList(booking.overview_polyline)
    return render(request, 'bookings/view-booking.html', {
        "booking":booking,
        "head_title":"Bookings Management",
        "GOOGLE_PLACES_KEY": env('GOOGLE_PLACES_KEY'),
        "first_station":first_station,
        "last_station":last_station,
        "inbetween_stations":inbetween_stations, 
        "polyline_coordinates":polyline_coordinates,
    })


@admins_only
@check_permissions('bookings.cancel_reasons_list')
def CancellationReasons(request):
    reasons = CancelReason.objects.all().order_by('-created_on')
    return render(request, 'cancellation-reasons/reasons-list.html', {
        "reasons":get_pagination(request, reasons),
        "head_title":"Cancellation Reasons Management",
    })


@admins_only
@check_permissions('bookings.add_cancel_reason')
def AddReason(request):
    if request.method == 'POST':
        if CancelReason.objects.filter(title=request.POST.get('title'),type_id=request.POST.get('type_id')):
            messages.error(request, 'Cancellation Reason with same title and type already exist.')
        else:
            CancelReason.objects.create(
                title=request.POST.get('title'),
                type_id=request.POST.get('type_id'),
                created_by = request.user, 
                is_active = True
            )
            messages.success(request, 'Cancellation Reason Added Successfully!')
        return redirect('bookings:cancellation_reasons')


@admins_only
@check_permissions('bookings.delete_cancel_reason')
def DeleteReason(request, id):
    reason = CancelReason.objects.get(id=id)
    if Rides.objects.filter(cancellation_reason=reason) or Booking.objects.filter(cancellation_reason=reason):
        messages.error(request, 'Reason is being used in some bookings so cannot be deleted at the moment')
    else:
        reason.delete()
        messages.success(request, 'Reason Deleted Successfully!')
    return redirect('bookings:cancellation_reasons')    


@admins_only
@check_permissions('bookings.activate_deactivate_reason')
def ActivateDeactivateReason(request):
    if request.method == 'POST':
        reason = CancelReason.objects.get(id=request.POST.get('reason_id'))
        if reason.is_active:
            reason.is_active = False
            reason.save()
            messages.success(request,'Cancellation Reason Deactivated Successfully')
        else:
            reason.is_active = True
            reason.save()
            messages.success(request,'Cancellation Reason Activated Successfully')
        return redirect('bookings:cancellation_reasons')   