from accounts.utils import *
from .serializer import *
from page.models import *
from .pagination import *
from accounts.models import *
from captains.models import *
from accounts.constants import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Q
from .utils import *
import datetime


class AssignedRides(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            captain = Captain.objects.get(user = request.user)
        except:
            return Response({"message":"Captain matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not(request.data.get('upcoming') or request.data.get('completed')):
            return Response({"message":"Please select the type of rides","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            selected_date = datetime.datetime.strptime(request.data.get('selected_date'), "%Y-%m-%d").date()
        except:
            return Response({"message":"Please select a valid date","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        
        rides = Rides.objects.filter(assigned_captain = captain, start_datetime__date = selected_date).order_by('-created_on')
        if int(request.data.get('upcoming')) == 1:
            rides = rides.filter(Q(ride_status = SCHEDULED_RIDE)|Q(ride_status = INPROGRESS_RIDE)|Q(ride_status = ARRIVED_AT_STATION)|Q(ride_status = STOPPED_RIDE))
        elif int(request.data.get('completed')) == 1:
            rides = rides.filter(Q(ride_status=CANCELLED_RIDE)|Q(ride_status=COMPLETED_RIDE))
        start,end,meta_data = GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None, rides)
        data = RidesListSerializer(rides[start : end],many=True,context={"request":request}).data
        return Response({"data":data,"meta":meta_data,"status": status.HTTP_200_OK}, status = status.HTTP_200_OK)


class AssignedRideDetails(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            ride = Rides.objects.get(id = request.data.get('ride_id'))
        except:
            return Response({"message":"Ride matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        data = RideDetailsSerializer(ride,many=False,context={"request":request}).data
        return Response({"data":data,"status": status.HTTP_200_OK}, status = status.HTTP_200_OK)
        

class StartRide(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            ride = Rides.objects.get(id = request.data.get('ride_id'))
        except:
            return Response({"message":"Ride matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not Booking.objects.filter(ride=ride):
            return Response({"message":"No Bookings Found On The Ride","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        else:
            ride.ride_status = INPROGRESS_RIDE
            ride.actual_start_datetime = datetime.datetime.now()
            ride.save()
            data = RideDetailsSerializer(ride,many=False,context={"request":request}).data
            return Response({"message":"Trip Started Successfully!","data":data,"status": status.HTTP_200_OK}, status = status.HTTP_200_OK)
        

class EndRide(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            ride = Rides.objects.get(id = request.data.get('ride_id'))
        except:
            return Response({"message":"Ride matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if Booking.objects.filter(ride=ride,status=BOOKED):
            return Response({"message":"You can not end the ride as all passengers have not either picked/dropped or missed yet.","status": status.HTTP_400_BAD_REQUEST}, status = status.HTTP_400_BAD_REQUEST)
        else:
            ride.ride_status = COMPLETED_RIDE
            ride.actual_end_datetime = datetime.datetime.now()
            ride.save()
            data = RideDetailsSerializer(ride,many=False,context={"request":request}).data
            return Response({"message":"Trip Completed Successfully!","data":data,"status": status.HTTP_200_OK}, status = status.HTTP_200_OK)


class StationPassengersList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            ride = Rides.objects.get(id = request.data.get('ride_id'))
        except:
            return Response({"message":"Ride matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        stations_data = []
        total_seats = sum([int(booking.seats_booked) for booking in Booking.objects.filter(ride=ride).exclude(status=CANCELLED_BOOKING)])
        route_stations = RoutesStations.objects.filter(route=ride.route).order_by('index')
        start,end,meta_data = GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None, route_stations)
        for station in route_stations[start : end]:
            station_bookings = Booking.objects.filter(Q(pickup_station=station.station, is_pickup=False)|Q(dropoff_station=station.station, is_pickup=True),status=BOOKED,ride=ride)
            stations_data.append({
                "station_id":station.station.id,
                "station_name":station.station.name,
                "bookings_data":StationBookingsSerializer(station_bookings,many=True,context={"request":request,"ride":ride}).data,
                "passengers_pickedup":Booking.objects.filter(Q(status=BOOKED)|Q(status=COMPLETE_BOOKING),pickup_station=station.station,is_pickup=True,ride=ride).count(),
                "passengers_dropedoff":Booking.objects.filter(Q(status=BOOKED)|Q(status=COMPLETE_BOOKING),ride=ride, dropoff_station=station.station,is_dropoff=True).count()
            })
        return Response({"stations_data":stations_data,"total_seats":total_seats,"meta_data":meta_data,"status": status.HTTP_200_OK}, status = status.HTTP_200_OK)


class ChangeBookingState(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            booking = Booking.objects.get(id = request.data.get('booking_id'))
        except:
            return Response({"message":"Booking matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if int(request.data.get('check_in')) == 1:
            booking.is_pickup = True
            booking.actual_pickup_station = request.data.get('actual_pickup_station') if request.data.get('actual_pickup_station') else None
            booking.actual_pickup_lattitude = request.data.get('actual_pickup_lattitude') if request.data.get('actual_pickup_lattitude') else None
            booking.actual_pickup_longitude = request.data.get('actual_pickup_longitude') if request.data.get('actual_pickup_longitude') else None
            booking.actual_pickup_time = datetime.datetime.now()
            booking.save()
            message = "Passenger Checked In Successfully!"
        elif int(request.data.get('check_out')) == 1:
            booking.is_dropoff = True
            booking.status = COMPLETE_BOOKING
            booking.actual_dropoff_station = request.data.get('actual_dropoff_station') if request.data.get('actual_dropoff_station') else None
            booking.actual_dropoff_lattitude = request.data.get('actual_dropoff_lattitude') if request.data.get('actual_dropoff_lattitude') else None
            booking.actual_dropoff_longitude = request.data.get('actual_dropoff_longitude') if request.data.get('actual_dropoff_longitude') else None
            booking.actual_dropoff_time = datetime.datetime.now()
            booking.save()
            message = "Passenger Checked Out Successfully!"
        elif int(request.data.get('missed')) == 1:
            booking.status = MISSED_BOOKING
            booking.save()
            message = "Passenger Missed!"
        else:
            return Response({"message":"Please select a valid state for booking","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        
        ## Pickup Station
        pickup_station = RoutesStations.objects.filter(route=booking.ride.route,station=booking.pickup_station).last()
        station_bookings = Booking.objects.filter(Q(pickup_station=pickup_station.station, is_pickup=False)|Q(dropoff_station=pickup_station.station, is_pickup=True),status=BOOKED,ride=booking.ride)
        pickup_station_data = {
            "station_id":pickup_station.station.id,
            "station_name":pickup_station.station.name,
            "bookings_data":StationBookingsSerializer(station_bookings,many=True,context={"request":request,"ride":booking.ride}).data,
            "passengers_pickedup":Booking.objects.filter(Q(status=BOOKED)|Q(status=COMPLETE_BOOKING),pickup_station=pickup_station.station,is_pickup=True,ride=booking.ride).count(),
            "passengers_dropedoff":Booking.objects.filter(Q(status=BOOKED)|Q(status=COMPLETE_BOOKING),ride=booking.ride, dropoff_station=pickup_station.station,is_dropoff=True).count()
        }

        ## Dropoff Station
        dropoff_station = RoutesStations.objects.filter(route=booking.ride.route,station=booking.dropoff_station).last()
        station_bookings = Booking.objects.filter(Q(pickup_station=dropoff_station.station, is_pickup=False)|Q(dropoff_station=dropoff_station.station, is_pickup=True),status=BOOKED,ride=booking.ride)
        dropoff_station_data = {
            "station_id":dropoff_station.station.id,
            "station_name":dropoff_station.station.name,
            "bookings_data":StationBookingsSerializer(station_bookings,many=True,context={"request":request,"ride":booking.ride}).data,
            "passengers_pickedup":Booking.objects.filter(Q(status=BOOKED)|Q(status=COMPLETE_BOOKING),pickup_station=dropoff_station.station,is_pickup=True,ride=booking.ride).count(),
            "passengers_dropedoff":Booking.objects.filter(Q(status=BOOKED)|Q(status=COMPLETE_BOOKING),ride=booking.ride, dropoff_station=dropoff_station.station,is_dropoff=True).count()
        }
        return Response({"message":message,"pickup_station_data":pickup_station_data,"dropoff_station_data":dropoff_station_data,"status": status.HTTP_200_OK}, status = status.HTTP_200_OK)


class UpdateRideLocation(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            ride = Rides.objects.get(id = request.data.get('ride_id'))
        except:
            return Response({"message":"Ride matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('latitude'):
            return Response({"message":"Please enter latitude","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('longitude'):
            return Response({"message":"Please enter longitude","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(id=request.user.id)
        user.latitude = request.data.get('latitude')
        user.longitude = request.data.get('longitude')
        user.save()
        ride.live_tracking = True
        ride.gps = True
        ride.latitude = request.data.get('latitude')
        ride.longitude = request.data.get('longitude')
        ride.save()
        data = {
            "ride_id":ride.id,
            "latitude":ride.latitude,
            "longitude":ride.longitude
        }
        return Response({"data":data,"status": status.HTTP_200_OK}, status = status.HTTP_200_OK)