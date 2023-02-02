import environ
import logging
from accounts.decorators import *
from accounts.helper import *
from accounts.utils import *
from .models import *
from frontend.views import *
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from datetime import datetime
env = environ.Env()
environ.Env.read_env()
db_logger = logging.getLogger('db')


@admins_only
@check_permissions('routes.schedules_list')
def SchedulesList(request):
    schedules = Schedules.objects.all().order_by('-created_on')

    if request.GET.get('route_name'):
        schedules = schedules.filter(route__route_name__icontains = request.GET.get('route_name'))
    if request.GET.get('start_station'):
        schedules = schedules.filter(route__start_station__address__icontains = request.GET.get('start_station'))
    if request.GET.get('end_station'):
        schedules = schedules.filter(route__end_station__address__icontains = request.GET.get('end_station'))
    if request.GET.get('start_time'):
        schedules = schedules.filter(start_time = request.GET.get('start_time'))
    if request.GET.get('is_active'):
        schedules = schedules.filter(is_active = request.GET.get('is_active'))
    if request.GET.get('schedule_price'):
        schedules = schedules.filter(schedule_price__icontains = request.GET.get('schedule_price'))

    schedules = get_pagination(request, schedules)
    if request.GET and not schedules:
        messages.error(request, 'No Data Found')
    return render(request, 'schedules/schedules-list.html', {
        "head_title":"Schedules Management",
        "schedules":schedules,
        "route_name": request.GET.get('route_name') if request.GET.get('route_name') else "",
        "start_station": request.GET.get('start_station') if request.GET.get('start_station') else "",
        "end_station": request.GET.get('end_station') if request.GET.get('end_station') else "",
        "start_time": request.GET.get('start_time') if request.GET.get('start_time') else "",
        "is_active": request.GET.get('is_active') if request.GET.get('is_active') else "",
        "schedule_price": request.GET.get('schedule_price') if request.GET.get('schedule_price') else ""
    })


@admins_only
@check_permissions('routes.add_schedule')
def AddSchedule(request):
    if request.method == 'POST':
        start_datetime = ConvertToUTC(datetime.combine(datetime.now().date(), datetime.strptime(request.POST.get('start_time'), '%H:%M').time()),request.POST.get('timezone'))
        route = Routes.objects.get(id=request.POST.get('route'))
        assigned_bus = Buses.objects.get(id=request.POST.get('bus')) 
        if Schedules.objects.filter(route = route,start_time = start_datetime.time(),assigned_bus = assigned_bus):
            messages.error(request, "An existing schedule for the same route, time and bus clashes with the added one!")
            return redirect('routes:add_schedule')
        else:
            schedule = Schedules.objects.create(
                route = route,
                start_station = route.start_station,
                end_station = route.end_station,
                start_time = start_datetime.time(),
                created_by = request.user,
                monday = True if 'monday' in request.POST.getlist('days[]') else False,
                tuesday = True if 'tuesday' in request.POST.getlist('days[]') else False,
                wednesday = True if 'wednesday' in request.POST.getlist('days[]') else False,
                thursday = True if 'thursday' in request.POST.getlist('days[]') else False,
                friday = True if 'friday' in request.POST.getlist('days[]') else False,
                saturday = True if 'saturday' in request.POST.getlist('days[]') else False,
                sunday = True if 'sunday' in request.POST.getlist('days[]') else False,
                price_overrided = True if request.POST.get('price_overrided') else False,
                arrival_allowance = request.POST.get('arrival_allowance'),
                departure_allowance = request.POST.get('departure_allowance'),
                base_fare = request.POST.get('base_fare'),
                max_fare = request.POST.get('max_fare'),
                max_seats_per_person = request.POST.get('max_seats_per_person'),
                base_distance = request.POST.get('base_distance'),
                distance_bucket_size = request.POST.get('distance_bucket_size'),
                distance_bucket_fare = request.POST.get('distance_bucket_fare'),
                time_bucket_size = request.POST.get('time_bucket_size'),
                time_bucket_fare = request.POST.get('time_bucket_fare'),
                timezone = request.POST.get('timezone'),
                category_type = request.POST.get('category_type'),
                flags = request.POST.get('flags'),
                assigned_bus = assigned_bus,
                assigned_captain = Captain.objects.get(user_id=request.POST.get('captains')),
                total_time_minutes = route.total_time_minutes,
                total_distance_km = route.total_distance_km,
                category = Category.objects.get(id=request.POST.get('category'))
            )
            schedule.schedule_price = CalculateScheduleFare(schedule,route.total_distance_km)
            schedule.save()
            messages.success(request, 'Schedule Added Successfully!')
            return redirect('routes:view_schedule',id=schedule.id)
    return render(request, 'schedules/add-schedule.html', {
        "head_title":"Schedules Management",
        "routes":Routes.objects.filter(is_active = True).order_by('-created_on'),
        "buses":Buses.objects.filter(is_active=True).order_by('-created_on'),
        "categories":Category.objects.all().order_by('-created_on')
    })


@admins_only
@check_permissions('routes.edit_schedule')
def EditSchedule(request, id):
    schedule = Schedules.objects.get(id=id)
    assigned_captains = AssignedCaptainBuses.objects.filter(bus=schedule.assigned_bus,captain__company__isnull=False).values_list('captain__user_id', flat=True)
    assigned_captain_users = User.objects.filter(id__in=assigned_captains)
    if Rides.objects.filter(schedule=schedule):
        messages.error(request, 'Rides exist on this schedule, so it cannot be updated at the moment.')
        return redirect('routes:view_schedule',id=schedule.id)
    if request.method == 'POST':
        start_datetime = ConvertToUTC(datetime.combine(datetime.now().date(), datetime.strptime(request.POST.get('start_time'), '%H:%M:%S').time()),request.POST.get('timezone'))
        route = Routes.objects.get(id=request.POST.get('route'))
        assigned_bus = Buses.objects.get(id=request.POST.get('bus'))
        if Schedules.objects.filter(route = route,start_time = start_datetime.time(),assigned_bus = assigned_bus).exclude(id=id):
            messages.error(request, "An existing schedule for the same route, time and bus clashes with the added one!")
            return redirect('routes:edit_schedule')
        else:
            schedule.route = route
            schedule.category = Category.objects.get(id=request.POST.get('category'))
            schedule.start_station = route.start_station
            schedule.end_station = route.end_station
            schedule.start_time = start_datetime.time()
            schedule.created_by = request.user
            schedule.monday = True if 'monday' in request.POST.getlist('days[]') else False
            schedule.tuesday = True if 'tuesday' in request.POST.getlist('days[]') else False
            schedule.wednesday = True if 'wednesday' in request.POST.getlist('days[]') else False
            schedule.thursday = True if 'thursday' in request.POST.getlist('days[]') else False
            schedule.friday = True if 'friday' in request.POST.getlist('days[]') else False
            schedule.saturday = True if 'saturday' in request.POST.getlist('days[]') else False
            schedule.sunday = True if 'sunday' in request.POST.getlist('days[]') else False
            schedule.price_overrided = True if request.POST.get('price_overrided') else False
            schedule.arrival_allowance = request.POST.get('arrival_allowance')
            schedule.departure_allowance = request.POST.get('departure_allowance')
            schedule.base_fare = request.POST.get('base_fare')
            schedule.max_fare = request.POST.get('max_fare')
            schedule.base_distance = request.POST.get('base_distance')
            schedule.distance_bucket_size = request.POST.get('distance_bucket_size')
            schedule.distance_bucket_fare = request.POST.get('distance_bucket_fare')
            schedule.time_bucket_size = request.POST.get('time_bucket_size')
            schedule.time_bucket_fare = request.POST.get('time_bucket_fare')
            schedule.max_seats_per_person = request.POST.get('max_seats_per_person')
            schedule.timezone = request.POST.get('timezone')
            schedule.category_type = request.POST.get('category_type')
            schedule.flags = request.POST.get('flags')
            schedule.assigned_captain = Captain.objects.get(user_id=request.POST.get('captains'))
            schedule.assigned_bus = assigned_bus
            schedule.total_time_minutes = route.total_time_minutes
            schedule.total_distance_km = route.total_distance_km
            schedule.save()
            schedule.schedule_price = CalculateScheduleFare(schedule,route.total_distance_km)
            schedule.save()
            messages.success(request, 'Schedule Updated Successfully!')
            return redirect('routes:view_schedule',id=schedule.id)
    return render(request, 'schedules/edit-schedule.html', {
        "head_title":"Schedules Management",
        "routes":Routes.objects.filter(is_active = True).order_by('-created_on'),
        "schedule":schedule,
        "buses":Buses.objects.filter(is_active=True),
        "captains":assigned_captain_users,
        "categories":Category.objects.all().order_by('-created_on')
    })


@admins_only
def ScheduleValidations(request):
    if request.is_ajax():
        data = {'present_time':False}
        start_time = datetime.combine(datetime.strptime(str(request.GET.get('start_date')), "%Y-%m-%d").date(), datetime.strptime(request.GET.get('start_time'), '%H:%M').time())
        current_time = datetime.strptime(str(ChangeToLocalTimezone(datetime.now(),request.GET.get("timezone"))), "%Y-%m-%d %H:%M:%S")
        if start_time < current_time:
            data['present_time'] = True
        return JsonResponse(data)


@admins_only
def GetPriceConfigurations(request):
    if request.is_ajax():
        category = Category.objects.get(id=request.GET.get('category_id'))
        return JsonResponse({
            "base_fare":category.base_fare,
            "max_fare":category.max_fare,
            "base_distance":category.base_distance,
            "distance_bucket_size":category.distance_bucket_size,
            "distance_bucket_fare":category.distance_bucket_fare,
            "time_bucket_size":category.time_bucket_size,
            "time_bucket_fare":category.time_bucket_fare,
            "max_seats_per_person":category.max_seats_per_person,
            "arrival_allowance":category.arrival_allowance,
            "departure_allowance":category.departure_allowance,
            "flags":category.flags,
            "category_type":category.category_type,
        })


@admins_only
@check_permissions('routes.view_schedule')
def ViewSchedule(request, id):
    schedule = Schedules.objects.get(id=id)
    route = Routes.objects.get(id=schedule.route_id)
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

    rides = Rides.objects.filter(schedule=schedule)
    return render(request, 'schedules/view-schedule.html', {
        "head_title":"Schedules Management",
        "schedule":schedule,
        "combinations":station_combinations, 
        "first_station":first_station,
        "last_station":last_station,
        "inbetween_stations":inbetween_stations, 
        "polyline_coordinates":polyline_coordinates,
        "GOOGLE_PLACES_KEY":env('GOOGLE_PLACES_KEY'),
        "rides":get_pagination(request, rides)
    })


@admins_only
@check_permissions('routes.delete_schedule')
def DeleteSchedule(request, id):
    schedule = Schedules.objects.get(id=id)
    if Rides.objects.filter(schedule=schedule):
        messages.error(request, 'Rides exist on this schedule, so it cannot be deleted at the moment.')
        return redirect('routes:view_schedule',id=schedule.id)
    else:
        schedule.delete()
    messages.success(request, "Schedule Deleted Successfully!")
    return redirect('routes:schedules_list')


@admins_only
@check_permissions('routes.activate_deactivate_schedule')
def ActivateInactivateSchedule(request):
    if request.method == 'POST':
        schedule = Schedules.objects.get(id=request.POST.get('schedule_id'))
        if schedule.is_active:
            schedule.is_active = False
            schedule.save()
            messages.success(request, "Schedule Deactivated Successfully!")
        else:
            schedule.is_active = True
            schedule.save()
            messages.success(request, "Schedule Activated Successfully!")
        return redirect('routes:view_schedule',id=schedule.id)