import requests
import json 
import polyline
from routes.models import *
from bookings.models import *
import logging
db_logger = logging.getLogger('db')


def GetDistanceMatrixData(origin_station, destination_station, API_KEY):
    origin_points = str(origin_station.latitude) + "%2C" + str(origin_station.longitude)
    destination_points = str(destination_station.latitude) + "%2C" + str(destination_station.longitude)
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin_points}&destinations={destination_points}&key={API_KEY}"
    response = requests.request("GET", url, headers={}, data={})
    data = json.loads(response.text)
    try:
        distance_meter  = data['rows'][0]['elements'][0]['distance']['value']
        distance_km = round(distance_meter/1000,1)
        time_second = int(data['rows'][0]['elements'][0]['duration']['value'])
        time_minutes = time_second//60
        return distance_km, time_minutes
    except:
        return None, None

def getLatLongList(polyline_data):
    if type(polyline_data) == str:
        polyline_data = [polyline_data]
    else:
        polyline_data = polyline_data
    if polyline_data:
        my_list = ''
        for p in polyline_data:
            x = polyline.decode(p)
            for i in x:
                my_list += '{"lat":' + str(i[0]) + ',"lng":' + str(i[1]) + '}#'
        return my_list
    else:
        return None

def GetPolylineData(route,API_KEY):
    all_stops_list = RoutesStations.objects.filter(route = route).order_by("index").values_list('id',flat=True)
    if len(all_stops_list) <= 25:
        start_station  = RoutesStations.objects.filter(route = route).order_by("index").first()
        start_coordinates = str(start_station.station.latitude)+","+str(start_station.station.longitude)
        end_station  = RoutesStations.objects.filter(route = route).order_by("index").last()
        end_coordinates = str(end_station.station.latitude)+","+str(end_station.station.longitude)
        all_stations = RoutesStations.objects.filter(route = route).order_by("index")
        waypoints_list = ""
        for station in all_stations:
            waypoints_list += "|" + str(station.station.latitude) + " " + str(station.station.longitude)
        url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start_coordinates}&waypoints=optimize:false{waypoints_list}&destination={end_coordinates}&sensor=false&key={API_KEY}&travelmode=driving"
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        distance_data = json.loads(response.text)
        try:
            main_polyline = distance_data['routes'][0]['overview_polyline']['points']
        except:
            main_polyline = None
    else:
        n = 24
        all_lists = [all_stops_list[i:i+n+1] for i in range(0, len(all_stops_list), n)]
        if len(all_lists[-1]) < 2:
            n = 2
            all_lists = [all_stops_list[i:i+n+1] for i in range(0, len(all_stops_list), n)]
        main_polyline = []
        for new_list in all_lists:
            start_station  = RoutesStations.objects.filter(route = route,id__in=new_list).order_by("index").first()
            start_coordinates = str(start_station.station.latitude)+","+str(start_station.station.longitude)
            end_station  = RoutesStations.objects.filter(route = route,id__in=new_list).order_by("index").last()
            end_coordinates = str(end_station.station.latitude)+","+str(end_station.station.longitude)
            all_stations = RoutesStations.objects.filter(route = route,id__in=new_list).order_by("index")
            waypoints_list = ""
            for station in all_stations:
                waypoints_list += "|" + str(station.station.latitude) + " " + str(station.station.longitude)
            url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start_coordinates}&waypoints=optimize:false{waypoints_list}&destination={end_coordinates}&sensor=false&key={API_KEY}&travelmode=driving"
            payload = {}
            headers = {}
            response = requests.request("GET", url, headers=headers, data=payload)
            distance_data = json.loads(response.text)
            try:
                main_polyline.append(distance_data['routes'][0]['overview_polyline']['points'])
            except:
                pass
            break
    main_route = Routes.objects.get(id=route.id)
    main_route.overview_polyline = main_polyline
    main_route.save()
    return main_polyline

def format_time(minutes):
    if (minutes // 60) > 0:
        return "{} hours {} minutes".format(minutes // 60, minutes % 60)
    else:
        return "{} minutes".format(minutes % 60)


def CalculateScheduleFare(schedule, distance):
    try:
        fare = round(float(schedule.base_fare) + ((float(distance) - float(schedule.base_distance))/float(schedule.distance_bucket_size)) * float(schedule.distance_bucket_fare),2)
        return fare if fare > 0 else 0
    except Exception as e:
        db_logger.exception(e)
        return 0


def GetBookingPolyline(booking,API_KEY):
    pickup_station = RoutesStations.objects.get(route = booking.route, station = booking.pickup_station)
    dropoff_station = RoutesStations.objects.get(route = booking.route, station = booking.dropoff_station)
    waypoints_list = ""
    waypoints_list += "|" + str(pickup_station.station.latitude) + " " + str(pickup_station.station.longitude)
    for station_index in range(int(pickup_station.index)+1,int(dropoff_station.index)):
        between_station = RoutesStations.objects.get(index=station_index,route=booking.route)
        waypoints_list += "|" + str(between_station.station.latitude) + " " + str(between_station.station.longitude)
    waypoints_list += "|" + str(dropoff_station.station.latitude) + " " + str(dropoff_station.station.longitude)

    pickup_coords = str(pickup_station.station.latitude)+","+str(pickup_station.station.longitude)
    dropoff_coords = str(dropoff_station.station.latitude)+","+str(dropoff_station.station.longitude)
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={pickup_coords}&waypoints=optimize:false{waypoints_list}&destination={dropoff_coords}&sensor=false&key={API_KEY}&travelmode=driving"
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    distance_data = json.loads(response.text)
    try:
        polyline = distance_data['routes'][0]['overview_polyline']['points']
    except:
        polyline = None
    booking.overview_polyline = polyline
    booking.save()
    return polyline