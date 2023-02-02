import environ
import logging
from accounts.decorators import *
from accounts.helper import *
from accounts.utils import *
from .models import *
from frontend.views import *
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import render, redirect
env = environ.Env()
environ.Env.read_env()
db_logger = logging.getLogger('db')


@admins_only
@check_permissions('routes.stations_list')
def StationsListView(request):
    stations = Stations.objects.all().order_by('-created_on')
    if request.GET.get('id'):
        stations = stations.filter(id = request.GET.get('id'))
    if request.GET.get('name'):
        stations = stations.filter(name__icontains = request.GET.get('name'))
    if request.GET.get('address'):
        stations = stations.filter(address__icontains = request.GET.get('address'))
    if request.GET.get('latitude'):
        stations = stations.filter(latitude__icontains = request.GET.get('latitude'))
    if request.GET.get('longitude'):
        stations = stations.filter(longitude__icontains = request.GET.get('longitude'))
    if request.GET.get('description'):
        stations = stations.filter(description__icontains = request.GET.get('description'))
    if request.GET.get('district'):
        stations = stations.filter(district__name__icontains = request.GET.get('district'))
    if request.GET.get('created_on'):
        stations = stations.filter(created_on__date = request.GET.get('created_on'))
    stations = get_pagination(request, stations)
    if request.GET and not stations:
        messages.error(request, 'No Data Found')
    return render(request, 'stations/stations-list.html', {
        "head_title":"Stations Management", 
        "stations":stations,
        "id": request.GET.get('id') if request.GET.get('id') else "",
        "name": request.GET.get('name') if request.GET.get('name') else "",
        "address": request.GET.get('address') if request.GET.get('address') else "",
        "latitude": request.GET.get('latitude') if request.GET.get('latitude') else "",
        "longitude": request.GET.get('longitude') if request.GET.get('longitude') else "",
        "district": request.GET.get('district') if request.GET.get('district') else "",
        "description": request.GET.get('description') if request.GET.get('description') else "",
        "created_on": request.GET.get('created_on') if request.GET.get('created_on') else "",
    })


@admins_only
@check_permissions('routes.add_station')
def AddStationView(request):
    if request.method == 'POST':
        latitude = request.POST.get('lat_long').split(',')[0]
        longitude = request.POST.get('lat_long').split(',')[1]
        if not latitude and longitude:
            messages.error(request, 'Please enter latitude and longitude.')
            return redirect('routes:stations_list')
        if Stations.objects.filter(latitude=latitude, longitude=longitude, address=request.POST.get('location')):
            messages.error(request, 'Station with Same Lattitude and Longitude Already exists')
            return redirect('routes:stations_list')
        station = Stations.objects.create(
            name = request.POST.get('name'),
            address = request.POST.get('location'),
            description = request.POST.get('description'),
            latitude = latitude,
            longitude = longitude,
            district = District.objects.get(id=request.POST.get('district'))
        )
        messages.success(request, 'Station Added Successfully!')
        return redirect('routes:view_station', id=station.id)
    return render(request, 'stations/add-station.html', {
        "head_title":"Stations Management", 
        "GOOGLE_PLACES_KEY":env('GOOGLE_PLACES_KEY'),
        "districts":District.objects.all().order_by('-created_on')
    })


@admins_only
@check_permissions('routes.view_station')
def ViewStation(request, id):
    station = Stations.objects.get(id=id)
    return render(request, 'stations/view-station.html', {"head_title":"Stations Management", "station":station,"GOOGLE_PLACES_KEY":env('GOOGLE_PLACES_KEY')})
    

@admins_only
@check_permissions('routes.delete_station')
def DeleteStation(request, id):
    station = Stations.objects.get(id=id)
    if RoutesStations.objects.filter(station=station):
        messages.success(request, 'Station Is Being Used In The Routes At The Moment, So Cannot Be Deleted!, ')
    else:
        station.delete()
    messages.success(request, 'Station Deleted Successfully!')
    return redirect('routes:stations_list')


@admins_only
@check_permissions('routes.routes_list')
def RoutesListView(request):
    routes = Routes.objects.filter(show=True).order_by('-created_on')
    if request.GET.get('route_name'):
        routes = routes.filter(route_name__icontains = request.GET.get('route_name'))
    if request.GET.get('description'):
        routes = routes.filter(description__icontains = request.GET.get('description'))
    if request.GET.get('city'):
        routes = routes.filter(city__name__icontains = request.GET.get('city'))
    if request.GET.get('start_station'):
        routes = routes.filter(start_station__address__icontains = request.GET.get('start_station'))
    if request.GET.get('end_station'):
        routes = routes.filter(end_station__address__icontains = request.GET.get('end_station'))
    if request.GET.get('is_active'):
        routes = routes.filter(is_active = request.GET.get('is_active'))
    if request.GET.get('created_on'):
        routes = routes.filter(created_on__date = request.GET.get('created_on'))
    routes = get_pagination(request, routes)
    if request.GET and not routes:
        messages.error(request, 'No Data Found')
    return render(request, 'routes/routes-list.html', {
        "head_title":"Routes Management", 
        "routes":routes,
        "route_name": request.GET.get('route_name') if request.GET.get('route_name') else "",
        "city": request.GET.get('city') if request.GET.get('city') else "",
        "start_station": request.GET.get('start_station') if request.GET.get('start_station') else "",
        "end_station": request.GET.get('end_station') if request.GET.get('end_station') else "",
        "description": request.GET.get('description') if request.GET.get('description') else "",
        "created_on": request.GET.get('created_on') if request.GET.get('created_on') else "",
        "is_active": request.GET.get('is_active') if request.GET.get('is_active') else "",
    })


@admins_only
@check_permissions('routes.add_route')
def AddRouteDetails(request):
    if request.method == 'POST':
        stations_list = request.POST.getlist('stations')
        if not stations_list:
            messages.error(request, 'Please select stations for the routes.')
            return redirect('routes:add_route_details')
        if len(stations_list) < 2:
            messages.error(request, 'Please select atleast 2 stations for the route')
            return redirect('routes:add_route_details')
        route = Routes.objects.create(
            route_name = request.POST.get('route_name'),
            city = Cities.objects.get(id=request.POST.get('city')),
            description = request.POST.get('description') if request.POST.get('description') else "",
            start_station = Stations.objects.get(id=stations_list[0]),
            end_station = Stations.objects.get(id=stations_list[-1]),
            timezone = request.POST.get('timezone')
        )
        [RoutesStations.objects.create(
            route = route, 
            station = Stations.objects.get(id=i),
            index = int(stations_list.index(i)) + 1
        ) for i in stations_list]

        combinations = [(a, b) for idx, a in enumerate(stations_list) for b in stations_list[idx + 1:]]
        for pair in combinations:
            station_one = Stations.objects.get(id=pair[0])
            station_two = Stations.objects.get(id=pair[1])
            distance_km, time_minutes = GetDistanceMatrixData(station_one, station_two, env('GOOGLE_PLACES_KEY'))
            if not distance_km and not time_minutes:
                RoutesStations.objects.filter(route = route).delete()
                route.delete()
                messages.error(request, "Could not retrieve driving distance between the selected stops.")
                return redirect('routes:add_route_details')
            else:
                RouteStationsCombination.objects.create(
                    from_station = station_one,
                    to_station = station_two,
                    time_minutes = time_minutes,
                    route = route,
                    distance_km = round(float(distance_km if distance_km else 0),2)
                )
                RoutesStations.objects.filter(route=route, station = station_two).update(
                    time_minutes = time_minutes,
                    distance_km = round(float(distance_km if distance_km else 0),2)
                )
        GetPolylineData(route, env('GOOGLE_PLACES_KEY'))
        return redirect('routes:add_route_stations', id=route.id)
    return render(request, 'routes/add-route/add-route-details.html', {
        "head_title":"Routes Management",
        "stations":Stations.objects.all().order_by('-created_on'),
        "cities":Cities.objects.all().order_by('-created_on'),
        "categories":Category.objects.all().order_by('-created_on')
    })


@admins_only
@check_permissions('routes.add_route')
def AddRouteStations(request,id):
    route = Routes.objects.get(id=id)
    if request.method == 'GET':
        stations_list = RoutesStations.objects.filter(route = route).order_by("index").values_list('station_id', flat=True)
        combinations = [((i), (i + 1) % len(stations_list)) for i in range(len(stations_list)-1)]
        first_station = RoutesStations.objects.filter(route = route).order_by("index").first()
        last_station = RoutesStations.objects.filter(route = route).order_by("index").last()
        start_station, end_station, distance_km, time_minutes, combination_ids = [], [], [], [], []
        for start, end in combinations:
            station1 = Stations.objects.get(id=stations_list[start])
            station2 = Stations.objects.get(id=stations_list[end])
            station_combination = RouteStationsCombination.objects.get(route = route, from_station = station1, to_station = station2)
            start_station.append(station1)
            end_station.append(station2)
            distance_km.append(station_combination.distance_km)
            time_minutes.append(station_combination.time_minutes)
            combination_ids.append(station_combination)
        stops_combinations = zip(start_station, end_station, distance_km, time_minutes,combination_ids)
        inbetween_stations = [str(i.station.latitude)+","+str(i.station.longitude) for i in RoutesStations.objects.filter(route = route).order_by("index").exclude(Q(id=first_station.id)|Q(id=last_station.id))]
        polyline_coordinates = getLatLongList(route.overview_polyline)
        return render(request, 'routes/add-route/add-route-stations.html', {"head_title":"Routes Management","stops_combinations":stops_combinations,"first_station":first_station,"last_station":last_station,"inbetween_stations":inbetween_stations, "polyline_coordinates":polyline_coordinates,"GOOGLE_PLACES_KEY":env('GOOGLE_PLACES_KEY'),"route":route})

    if request.method == 'POST':
        for i in range(0, len(request.POST.getlist('combination_id'))):
            combination = RouteStationsCombination.objects.get(id=request.POST.getlist('combination_id')[i])
            if int(request.POST.getlist('minutes')[i]) >= int(combination.time_minutes):
                combination.time_minutes = request.POST.getlist('minutes')[i]
                combination.break_time_minutes = request.POST.getlist('break_time_minutes')[i]
                combination.save()
            else:
                messages.error(request, 'Timing between 2 stops can not be less then predicted time.')
                return redirect('routes:add_route_stations', id=route.id)
        stations_list = RoutesStations.objects.filter(route = route).order_by("index").values_list('station_id', flat=True)
        combinations = [((i), (i + 1) % len(stations_list)) for i in range(len(stations_list)-1)]
        total_kms, total_time, break_time = [], [], []
        for start, end in combinations:
            station1 = Stations.objects.get(id=stations_list[start])
            station2 = Stations.objects.get(id=stations_list[end])
            combo = RouteStationsCombination.objects.get(route = route, from_station = station1, to_station = station2)
            total_kms.append(float(combo.distance_km if combo.distance_km else 0))
            total_time.append(int(combo.time_minutes if combo.time_minutes else 0))
            break_time.append(int(combo.break_time_minutes if combo.break_time_minutes else 0))
        route.total_distance_km = sum(total_kms)
        route.total_time_minutes = sum(total_time) + sum(break_time)
        route.show = True
        route.save()
        messages.success(request, "Route Added Successfully!")
        return redirect('routes:view_route', id=route.id)


@admins_only
@check_permissions('routes.view_route')
def ViewRoute(request, id):
    route = Routes.objects.get(id=id)
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

    schedules = Schedules.objects.filter(route = route)
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
    return render(request, 'routes/view-route.html', {
        "head_title":"Routes Management","route":route, "combinations":station_combinations, 
        "first_station":first_station,"last_station":last_station,"inbetween_stations":inbetween_stations, 
        "polyline_coordinates":polyline_coordinates,              
        "GOOGLE_PLACES_KEY":env('GOOGLE_PLACES_KEY'),"schedules":get_pagination(request, schedules),
        "route_name": request.GET.get('route_name') if request.GET.get('route_name') else "",
        "start_station": request.GET.get('start_station') if request.GET.get('start_station') else "",
        "end_station": request.GET.get('end_station') if request.GET.get('end_station') else "",
        "start_time": request.GET.get('start_time') if request.GET.get('start_time') else "",
        "is_active": request.GET.get('is_active') if request.GET.get('is_active') else "",
        "schedule_price": request.GET.get('schedule_price') if request.GET.get('schedule_price') else ""
    })


@admins_only
@check_permissions('routes.delete_route')
def DeleteRoute(request, id):
    route = Routes.objects.get(id=id)
    if Schedules.objects.filter(route=route):
        messages.error(request, 'Schedules exist on this route, so it cannot be deleted at the moment.')
        return redirect('routes:view_route', id=route.id)
    else:
        RoutesStations.objects.filter(route=route).delete()
        RouteStationsCombination.objects.filter(route=route).delete()
        route.delete()
        messages.success(request, 'Route Deleted Successfully!')
        return redirect('routes:routes_list')


@admins_only
@check_permissions('routes.activate_deactivate_route')
def ActivateInactivateRoute(request):
    if request.method == 'POST':
        route = Routes.objects.get(id=request.POST.get('route_id'))
        if route.is_active:
            route.is_active = False
            route.save()
            messages.success(request, "Route Deactivated Successfully!")
        else:
            route.is_active = True
            route.save()
            messages.success(request, "Route Activated Successfully!")
        return redirect('routes:view_route', id=route.id)


@admins_only
@check_permissions('routes.edit_route')
def EditRouteDetails(request, id):
    route = Routes.objects.get(id=id)
    if Schedules.objects.filter(route=route):
        messages.error(request, 'Schedules exist on this route, so it cannot be updated at the moment.')
        return redirect('routes:view_route', id=route.id)
    if request.method == 'POST':
        stations_list = request.POST.getlist('stations')
        if not stations_list:
            messages.error(request, 'Please select stations for the routes.')
            return redirect('routes:edit_route_details')
        if len(stations_list) < 2:
            messages.error(request, 'Please select atleast 2 stations for the route')
            return redirect('routes:edit_route_details')
        route.route_name = request.POST.get('route_name')
        route.city = Cities.objects.get(id=request.POST.get('city'))
        route.description = request.POST.get('description') if request.POST.get('description') else ""
        route.start_station = Stations.objects.get(id=stations_list[0])
        route.end_station = Stations.objects.get(id=stations_list[-1])
        route.timezone = request.POST.get('timezone')
        route.save()

        RoutesStations.objects.filter(route = route).delete()
        [RoutesStations.objects.create(
            route = route, 
            station = Stations.objects.get(id=i),
            index = int(stations_list.index(i)) + 1
        ) for i in stations_list]

        combinations = [(a, b) for idx, a in enumerate(stations_list) for b in stations_list[idx + 1:]]
        RouteStationsCombination.objects.filter(route = route).delete()
        for pair in combinations:
            station_one = Stations.objects.get(id=pair[0])
            station_two = Stations.objects.get(id=pair[1])
            distance_km, time_minutes = GetDistanceMatrixData(station_one, station_two, env('GOOGLE_PLACES_KEY'))
            if not distance_km and not time_minutes:
                RoutesStations.objects.filter(route = route).delete()
                messages.error(request, "Could not retrieve driving distance between the selected stops.")
                return redirect('routes:edit_route_details')
            else:
                RouteStationsCombination.objects.create(
                    from_station = station_one,
                    to_station = station_two,
                    time_minutes = time_minutes,
                    route = route,
                    distance_km = round(float(distance_km if distance_km else 0),2)
                )
                RoutesStations.objects.filter(route=route, station = station_two).update(
                    time_minutes = time_minutes,
                    distance_km = round(float(distance_km if distance_km else 0),2)
                )
        GetPolylineData(route, env('GOOGLE_PLACES_KEY'))
        return redirect('routes:edit_route_stations', id=route.id)
    station_idss = RoutesStations.objects.filter(route=route).order_by('index').values_list('station_id', flat=True)
    return render(request, 'routes/edit-route/edit-route-details.html', {
        "head_title":"Routes Management",
        "stations":Stations.objects.all().exclude(id__in=station_idss),
        "cities":Cities.objects.all().order_by('-created_on'),
        "route":route,
        "categories":Category.objects.all().order_by('-created_on'),
        "route_stations":RoutesStations.objects.filter(route=route).order_by('index')
    })


@admins_only
@check_permissions('routes.edit_route')
def EditRouteStations(request,id):
    route = Routes.objects.get(id=id)
    if request.method == 'GET':
        stations_list = RoutesStations.objects.filter(route = route).order_by("index").values_list('station_id', flat=True)
        combinations = [((i), (i + 1) % len(stations_list)) for i in range(len(stations_list)-1)]
        first_station = RoutesStations.objects.filter(route = route).order_by("index").first()
        last_station = RoutesStations.objects.filter(route = route).order_by("index").last()
        start_station, end_station, distance_km, time_minutes, combination_ids = [], [], [], [], []
        for start, end in combinations:
            station1 = Stations.objects.get(id=stations_list[start])
            station2 = Stations.objects.get(id=stations_list[end])
            station_combination = RouteStationsCombination.objects.get(route = route, from_station = station1, to_station = station2)
            start_station.append(station1)
            end_station.append(station2)
            distance_km.append(station_combination.distance_km)
            time_minutes.append(station_combination.time_minutes)
            combination_ids.append(station_combination)
        stops_combinations = zip(start_station, end_station, distance_km, time_minutes,combination_ids)
        inbetween_stations = [str(i.station.latitude)+","+str(i.station.longitude) for i in RoutesStations.objects.filter(route = route).order_by("index").exclude(Q(id=first_station.id)|Q(id=last_station.id))]
        polyline_coordinates = getLatLongList(route.overview_polyline)
        return render(request, 'routes/edit-route/edit-route-stations.html', {"head_title":"Routes Management","stops_combinations":stops_combinations,"first_station":first_station,"last_station":last_station,"inbetween_stations":inbetween_stations, "polyline_coordinates":polyline_coordinates,"GOOGLE_PLACES_KEY":env('GOOGLE_PLACES_KEY'),"route":route})

    if request.method == 'POST':
        for i in range(0, len(request.POST.getlist('combination_id'))):
            combination = RouteStationsCombination.objects.get(id=request.POST.getlist('combination_id')[i])
            if int(request.POST.getlist('minutes')[i]) >= int(combination.time_minutes):
                combination.time_minutes = request.POST.getlist('minutes')[i]
                combination.break_time_minutes = request.POST.getlist('break_time_minutes')[i]
                combination.save()
            else:
                messages.error(request, 'Timing between 2 stops can not be less then predicted time.')
                return redirect('routes:edit_route_stations', id=route.id)
        stations_list = RoutesStations.objects.filter(route = route).order_by("index").values_list('station_id', flat=True)
        combinations = [((i), (i + 1) % len(stations_list)) for i in range(len(stations_list)-1)]
        total_kms, total_time, break_time = [], [], []
        for start, end in combinations:
            station1 = Stations.objects.get(id=stations_list[start])
            station2 = Stations.objects.get(id=stations_list[end])
            combo = RouteStationsCombination.objects.get(route = route, from_station = station1, to_station = station2)
            total_kms.append(float(combo.distance_km if combo.distance_km else 0))
            total_time.append(int(combo.time_minutes if combo.time_minutes else 0))
            break_time.append(int(combo.break_time_minutes if combo.break_time_minutes else 0))
        route.total_distance_km = sum(total_kms)
        route.total_time_minutes = sum(total_time) + sum(break_time)
        route.show = True
        route.save()
        messages.success(request, "Route Updated Successfully!")
        return redirect('routes:view_route', id=route.id)
        
        
        
        