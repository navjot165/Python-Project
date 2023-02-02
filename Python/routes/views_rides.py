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
from django.http import JsonResponse
from django.shortcuts import render, redirect
from datetime import datetime, timedelta
env = environ.Env()
environ.Env.read_env()
db_logger = logging.getLogger('db')


@admins_only
@check_permissions('routes.rides_list')
def RidesList(request):
    rides = Rides.objects.all().order_by('-created_on')
    if request.GET.get('route_name'):
        rides = rides.filter(route__route_name__icontains = request.GET.get('route_name'))
    if request.GET.get('start_station'):
        rides = rides.filter(route__start_station__address__icontains = request.GET.get('start_station'))
    if request.GET.get('end_station'):
        rides = rides.filter(route__end_station__address__icontains = request.GET.get('end_station'))
    if request.GET.get('start_datetime'):
        rides = rides.filter(start_datetime__date = request.GET.get('start_datetime'))
    if request.GET.get('assigned_bus'):
        rides = rides.filter(assigned_bus__plate_number__icontains = request.GET.get('assigned_bus'))
    if request.GET.get('assigned_captain'):
        rides = rides.filter(assigned_captain__user__full_name__icontains = request.GET.get('assigned_captain'))
    if request.GET.get('ride_price'):
        rides = rides.filter(ride_price__icontains = request.GET.get('ride_price'))
    if request.GET.get('ride_status'):
        rides = rides.filter(ride_status = request.GET.get('ride_status'))
    if request.GET and not rides:
        messages.error(request, 'No Data Found')
    return render(request, 'rides/rides-list.html', {
        "head_title":"Rides Management",
        "rides":get_pagination(request, rides),
        "route_name": request.GET.get('route_name') if request.GET.get('route_name') else "",
        "start_station": request.GET.get('start_station') if request.GET.get('start_station') else "",
        "end_station": request.GET.get('end_station') if request.GET.get('end_station') else "",
        "start_datetime": request.GET.get('start_datetime') if request.GET.get('start_datetime') else "",
        "assigned_bus": request.GET.get('assigned_bus') if request.GET.get('assigned_bus') else "",
        "assigned_captain": request.GET.get('assigned_captain') if request.GET.get('assigned_captain') else "",
        "ride_price": request.GET.get('ride_price') if request.GET.get('ride_price') else "",
        "ride_status": request.GET.get('ride_status') if request.GET.get('ride_status') else "",
    })


@admins_only
@check_permissions('routes.add_ride')
def AddRide(request):
    if request.GET.get('schedule_id'):
        selected_schedule = Schedules.objects.get(id=request.GET.get('schedule_id'))
    else:
        selected_schedule = None
    if request.method == 'POST':
        start_datetime = ConvertToUTC(datetime.combine(datetime.strptime(str(request.POST.get('start_date')), "%m/%d/%Y").date(), datetime.strptime(request.POST.get('start_time'), '%H:%M:%S').time()),request.POST.get('timezone'))
        route = Routes.objects.get(id=request.POST.get('route'))
        schedule = Schedules.objects.get(id=request.POST.get('schedule'))
        end_datetime = timedelta(minutes=int(route.total_time_minutes))+start_datetime
        ride = Rides.objects.create(
            start_datetime = start_datetime,
            end_datetime = end_datetime, 
            dispatch_type = MANUAL,
            schedule = schedule,
            route = route,
            ride_price = schedule.schedule_price,
            assigned_captain = schedule.assigned_captain,
            is_manual = True,
            is_emergency = request.POST.get('is_emergency'),
            is_confirmed = True,
            start_ride_station = schedule.start_station,
            end_ride_station = schedule.end_station,
            price_config = CUSTOM_PRICE if schedule.price_overrided else CATEGORY_PRICE,
            assigned_bus = schedule.assigned_bus,
            created_by = request.user,
            timezone = request.POST.get('timezone'),
            total_seats = schedule.assigned_bus.bus_type.seat_count,
            seats_left = schedule.assigned_bus.bus_type.seat_count,
            category_type = schedule.category_type,
            flags = schedule.flags,
            max_seats_per_person = schedule.max_seats_per_person,
            arrival_allowance = schedule.arrival_allowance,
            departure_allowance = schedule.departure_allowance,
        )
        try:
            ride.full_clean()
            messages.success(request, "Ride Added Successfully!")
            return redirect('routes:view_ride', id=ride.id)
        except ValidationError as e:
            ride.delete()
            messages.success(request,'; '.join(e.messages))
            return redirect('routes:add_ride')
    return render(request, 'rides/add-ride.html', {
        "head_title":"Rides Management",
        "routes":Routes.objects.filter(is_active=True),
        "selected_schedule":selected_schedule if selected_schedule else None
    }) 


@admins_only
def GetRouteSchedules(request):
    if request.is_ajax():
        data = []
        schedules = Schedules.objects.filter(route_id=request.GET.get('route_id'))
        if schedules:
            for schedule in schedules:
                data.append({
                    "id":schedule.id,
                    "start_time":datetime.strptime(str(ChangeToLocalTimezone(datetime.combine(datetime.now().date(), schedule.start_time),request.GET.get('timezone')).split('+')[0]), "%Y-%m-%d %H:%M:%S").time().strftime('%H:%M')
                })
            return JsonResponse(data, safe=False)
        else:
            return JsonResponse(data, safe=False)


@admins_only
def GetAssignedCaptains(request):
    if request.is_ajax():
        bus = Buses.objects.get(id=request.GET.get('bus_id'))
        assigned_captains = AssignedCaptainBuses.objects.filter(bus=bus, captain__company__isnull=False).values_list('captain__user_id', flat=True)
        users = User.objects.filter(id__in=assigned_captains)
        if users:
            return JsonResponse([{
                "id":user.id,
                "full_name":user.full_name if user.full_name else str(user.country_code) + str(user.mobile_no)
            } for user in users], safe=False)
        else:
            return JsonResponse([], safe=False)


@admins_only
def GetScheduleDays(request):
    if request.is_ajax():
        schedule = Schedules.objects.get(id=request.GET.get('schedule_id'))
        days = []
        days_name = ""
        if schedule.sunday:
            days.append(0)
            days_name += 'Sun, '
        if schedule.monday:
            days.append(1)
            days_name += 'Mon, '
        if schedule.tuesday:
            days.append(2)
            days_name += 'Tues, '
        if schedule.wednesday:
            days.append(3)
            days_name += 'Wed, '
        if schedule.thursday:
            days.append(4)
            days_name += 'Thurs, '
        if schedule.friday:
            days.append(5)
            days_name += 'Fri, '
        if schedule.saturday:
            days.append(6)
            days_name += 'Sat, '
        days_name = days_name[:len(days_name) - 2]
        if schedule.assigned_bus:
            bus_data = {
                "id":schedule.assigned_bus.id,
                "plate_number":schedule.assigned_bus.plate_number
            }
        else:
            bus_data = {}
        if schedule.assigned_captain:
            captain_data = {
                "id":schedule.assigned_captain.user.id,
                "name":schedule.assigned_captain.user.full_name if schedule.assigned_captain.user.full_name else str(schedule.assigned_captain.user.country_code) + str(schedule.assigned_captain.user.mobile_no)
            }
        else:
            captain_data = {}
        return JsonResponse({"days":days,"days_name":days_name,"bus_data":bus_data,"captain_data":captain_data}, safe=False)


@admins_only
@check_permissions('routes.edit_ride')
def ViewRide(request, id):
    ride = Rides.objects.get(id=id)
    route = Routes.objects.get(id=ride.route_id)
    stations_list = RoutesStations.objects.filter(route = route).order_by("index").values_list('station_id', flat=True)
    combinations = [((i), (i + 1) % len(stations_list)) for i in range(len(stations_list)-1)]
    first_station = RoutesStations.objects.filter(route = route).order_by("index").first()
    last_station = RoutesStations.objects.filter(route = route).order_by("index").last()
    station_combinations = []
    for start, end in combinations:
        station1 = Stations.objects.get(id=stations_list[start])
        station2 = Stations.objects.get(id=stations_list[end])
        combo = RouteStationsCombination.objects.get(route = route, from_station = station1, to_station = station2)
        station_combinations.append(combo)
    inbetween_stations = [str(i.station.latitude)+","+str(i.station.longitude) for i in RoutesStations.objects.filter(route = route).order_by("index").exclude(Q(id=first_station.id)|Q(id=last_station.id))]
    polyline_coordinates = getLatLongList(route.overview_polyline)
    return render(request, 'rides/view-ride.html',{
        "head_title":"Rides Management",
        "ride":ride,
        "combinations":station_combinations, 
        "first_station":first_station,
        "last_station":last_station,
        "inbetween_stations":inbetween_stations, 
        "polyline_coordinates":polyline_coordinates,
        "GOOGLE_PLACES_KEY":env('GOOGLE_PLACES_KEY')
    })


@admins_only
@check_permissions('routes.delete_ride')
def DeleteRide(request, id):
    ride = Rides.objects.get(id=id)
    if Booking.objects.filter(ride=ride):
        messages.error(request, 'Bookings exist on this ride, so it cannot be deleted at the moment.')
        return redirect('routes:view_ride', id=ride.id)
    else:
        ride.delete()
        messages.success(request, 'Ride Deleted Successfully!')
        return redirect('routes:rides_list')


@admins_only
@check_permissions('routes.view_ride')
def EditRide(request, id):
    ride = Rides.objects.get(id=id)
    if Booking.objects.filter(ride=ride):
        messages.error(request, 'Bookings exist on this ride, so it cannot be updated at the moment.')
        return redirect('routes:view_ride', id=ride.id)
    schedule_id, schedule_time = [],[]
    for schedule in Schedules.objects.filter(route=ride.route.id):
        schedule_id.append(schedule.id)
        schedule_time.append(datetime.strptime(str(ChangeToLocalTimezone(datetime.combine(datetime.now().date(), schedule.start_time),schedule.timezone).split('+')[0]), "%Y-%m-%d %H:%M:%S").time().strftime('%H:%M'))

    if request.method == 'POST':
        start_datetime = ConvertToUTC(datetime.combine(datetime.strptime(str(request.POST.get('start_date')), "%m/%d/%Y").date(), datetime.strptime(request.POST.get('start_time'), '%H:%M:%S').time()),request.POST.get('timezone'))
        route = Routes.objects.get(id=request.POST.get('route'))
        schedule = Schedules.objects.get(id=request.POST.get('schedule'))
        end_datetime = timedelta(minutes=int(route.total_time_minutes))+start_datetime
        if Rides.objects.filter(Q(start_datetime__lte=start_datetime, end_datetime__gte=start_datetime) | Q(start_datetime__lte=end_datetime, end_datetime__gte=end_datetime), route=ride.route, schedule=ride.schedule, assigned_bus=ride.assigned_bus).exclude(id=id):
            messages.error(request, 'An existing ride for the same route, schedule and bus clashes with the added one!')
            return redirect('routes:edit_ride', id=ride.id)
        else:
            ride.start_datetime = start_datetime
            ride.end_datetime = end_datetime
            ride.dispatch_type = MANUAL
            ride.schedule = schedule
            ride.route = route
            ride.ride_price = schedule.schedule_price
            ride.assigned_captain = schedule.assigned_captain
            ride.is_manual = True
            ride.is_emergency = request.POST.get('is_emergency')
            ride.is_confirmed = True
            ride.start_ride_station = schedule.start_station
            ride.end_ride_station = schedule.end_station
            ride.price_config = CUSTOM_PRICE if schedule.price_overrided else CATEGORY_PRICE
            ride.assigned_bus = schedule.assigned_bus
            ride.timezone = request.POST.get('timezone')
            ride.total_seats = schedule.assigned_bus.bus_type.seat_count
            ride.seats_left = schedule.assigned_bus.bus_type.seat_count
            ride.category_type = schedule.category_type
            ride.flags = schedule.flags
            ride.max_seats_per_person = schedule.max_seats_per_person
            ride.arrival_allowance = schedule.arrival_allowance
            ride.departure_allowance = schedule.departure_allowance
            ride.save()
            messages.success(request, "Ride Updated Successfully!")
            return redirect('routes:view_ride', id=ride.id)
    return render(request, 'rides/edit-ride.html', {
        "head_title":"Rides Management",
        "ride":ride,
        "routes":Routes.objects.filter(is_active=True),
        "schedules":zip(schedule_id, schedule_time)
    })


@admins_only
@check_permissions('routes.ride_search_list')
def RidesSearchHistoryList(request):
    searches = UserRideSearch.objects.all().order_by('-created_on')
    if request.GET.get('full_name'):
        searches = searches.filter(user__full_name__icontains = request.GET.get('full_name'))
    if request.GET.get('pickup_address'):
        searches = searches.filter(pickup_address__icontains = request.GET.get('pickup_address'))
    if request.GET.get('dropoff_address'):
        searches = searches.filter(dropoff_address__icontains = request.GET.get('dropoff_address'))
    if request.GET.get('search_count'):
        searches = searches.filter(search_count = request.GET.get('search_count'))
    if request.GET.get('is_ride_available'):
        searches = searches.filter(is_ride_available = request.GET.get('is_ride_available'))
    if request.GET.get('is_pickup_available'):
        searches = searches.filter(is_pickup_available = request.GET.get('is_pickup_available'))
    if request.GET.get('is_dropoff_available'):
        searches = searches.filter(is_dropoff_available = request.GET.get('is_dropoff_available'))
    if request.GET and not searches:
        messages.error(request, 'No Data Found')
    return render(request, 'search-history/search-history-list.html', {
        "head_title":"Rides Search History",
        "searches":get_pagination(request, searches),
        "full_name": request.GET.get('full_name') if request.GET.get('full_name') else "",
        "pickup_address": request.GET.get('pickup_address') if request.GET.get('pickup_address') else "",
        "dropoff_address": request.GET.get('dropoff_address') if request.GET.get('dropoff_address') else "",
        "search_count": request.GET.get('search_count') if request.GET.get('search_count') else "",
        "is_ride_available": request.GET.get('is_ride_available') if request.GET.get('is_ride_available') else "",
        "is_pickup_available": request.GET.get('is_pickup_available') if request.GET.get('is_pickup_available') else "",
        "is_dropoff_available": request.GET.get('is_dropoff_available') if request.GET.get('is_dropoff_available') else "",
    })


@admins_only
@check_permissions('routes.view_ride_search')
def ViewSearchHistory(request, id):
    search = UserRideSearch.objects.get(id=id)
    return render(request, 'search-history/view-search-history.html', {
        "head_title":"Rides Search History",
        "search":search,
    })


@admins_only
@check_permissions('routes.delete_ride_search')
def DeleteSearchHistory(request,id):
    UserRideSearch.objects.get(id=id).delete()
    messages.success(request, 'Search History Deleted Successfully!')
    return redirect('routes:rides_search_history')


@admins_only
@check_permissions('routes.clear_ride_search')
def ClearSearchHistory(request):
    search_history = UserRideSearch.objects.all()
    if search_history:
        search_history.delete()
        messages.success(request, 'Search History Cleared Successfully!')
    else:
        messages.success(request, 'No Search History Found!')
    return redirect('routes:rides_search_history')


@admins_only
@check_permissions('routes.cancel_ride')
def CancelRide(request, id):
    ride = Rides.objects.get(id=id)
    if request.method == 'POST':
        if ride.ride_status == SCHEDULED_RIDE:
            ride.ride_status = CANCELLED_RIDE
            ride.cancelled_by = request.user
            ride.cancelled_at = datetime.now()
            ride.cancellation_reasons.add(SelectedCancelReason.objects.create(reason=request.POST.get('reason').strip()))
            ride.save()
            ride_bookings = Booking.objects.filter(status=BOOKED,ride=ride)
            if ride_bookings:
                for booking in ride_bookings:
                    booking.status = CANCELLED_BOOKING
                    booking.cancelled_by = request.user
                    booking.cancelled_at = datetime.now()
                    booking.cancellation_reasons.add(SelectedCancelReason.objects.create(reason=request.POST.get('reason').strip()))
                    booking.refund_amount = booking.booking_price
                    booking.save()
                    ride.seats_left = int(ride.seats_left if ride.seats_left else 0) + int(booking.seats_booked if booking.seats_booked else 0)
                    ride.save()
            messages.success(request,"Ride Cancelled Successfully!")
        else:
            messages.success(request,"Sorry! You cannot cancel ride in this state!")
    return redirect('routes:view_ride',id=ride.id)