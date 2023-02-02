from accounts.models import *
from captains.models import *
from page.models import *
from contact_us.models import *
from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField
from routes.models import *
from bookings.models import *
from reviews.models import *
from accounts.helper import CalculateScheduleFare
import datetime


class Imageserializer(ModelSerializer):
	class Meta:
		model = Image
		fields = ('id','upload')


class UserSerializer(ModelSerializer):
    profile_completion_percent = SerializerMethodField(read_only = True)
    average_rating = SerializerMethodField(read_only = True)
    city = SerializerMethodField(read_only = True)
    class Meta:
        model = User
        fields = ('id','full_name','first_name','last_name','email','mobile_no','country_code','status','profile_pic','role_id','temp_otp','otp_verified','gender','referral_code','profile_completion_percent','average_rating','is_profile_verified','city')

    def get_profile_completion_percent(self, obj):
        full_name = 1 if obj.full_name else 0
        mobile_no = 1 if obj.mobile_no else 0
        email = 1 if obj.email else 0
        gender = 1 if obj.gender else 0
        profile_pic = 1 if obj.profile_pic else 0
        try:
            return int(((full_name + mobile_no + email + gender + profile_pic)/5)*100)
        except:
            return 0

    def get_average_rating(self, obj):
        return round(float(obj.average_rating if obj.average_rating else 0),1)
    
    def get_city(self, obj):
        if obj.city:
            return {"id":obj.city.id, "name":obj.city.name} if obj.city else {}
        else:
            default_city = Cities.objects.filter(default=True).last()
            return {"id":default_city.id, "name":default_city.name} if default_city else {}


class CaptainSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)
    driving_license = Imageserializer(many=True,read_only=True)
    govt_id_proof = Imageserializer(many=True,read_only=True)
    profile_completion_percent = SerializerMethodField(read_only = True)
    class Meta:
        model = Captain
        fields = ('id','user','is_blacklisted','years_of_experience','driving_license_expiry_date','driving_license','govt_id_proof','profile_completion_percent')

    def get_profile_completion_percent(self, obj):
        full_name = 1 if obj.user.full_name else 0
        mobile_no = 1 if obj.user.mobile_no else 0
        email = 1 if obj.user.email else 0
        gender = 1 if obj.user.gender else 0
        profile_pic = 1 if obj.user.profile_pic else 0
        years_of_experience = 1 if obj.years_of_experience else 0
        driving_license_expiry_date = 1 if obj.driving_license_expiry_date else 0
        driving_license = 1 if Captain.driving_license.through.objects.filter(captain_id = obj.id) else 0
        govt_id_proof = 1 if Captain.govt_id_proof.through.objects.filter(captain_id = obj.id) else 0
        try:
            return int(((full_name + mobile_no + email + gender + profile_pic + years_of_experience + driving_license_expiry_date + driving_license + govt_id_proof)/9)*100)
        except:
            return 0


class PagesSerializer(ModelSerializer):
    class Meta:
        model = Pages
        fields = ('type_id','title','content')


class ContactUsSerializer(ModelSerializer):
    class Meta:
        model = ContactUs
        fields = '__all__'


class RoutesListSerializer(ModelSerializer):
    start_station = CharField(source='start_station.name')
    end_station = CharField(source='end_station.name')
    recent_trip = SerializerMethodField(read_only = True)
    recent_trip_details = SerializerMethodField(read_only = True)
    city = SerializerMethodField(read_only = True)
    
    class Meta:
        model = Routes
        fields = ('id', 'route_name', 'start_station', 'end_station', 'recent_trip','city','recent_trip_details')

    def get_recent_trip(self, obj):
        booking = Booking.objects.filter(created_by=self.context.get('request').user, status=COMPLETE_BOOKING).order_by('updated_on').last() 
        if booking:
            return True if booking.route_id == obj.id else False
        else:
            return False

    def get_recent_trip_details(self, obj):
        request = self.context.get('request')
        booking = Booking.objects.filter(created_by=request.user, status=COMPLETE_BOOKING).order_by('updated_on').last() 
        if booking:
            if booking.route_id == obj.id:
                return {
                    "route":booking.route.id,
                    "pickup_station":{
                        "id":booking.pickup_station.id,
                        "address":booking.pickup_station.name,
                        "latitude":booking.pickup_station.latitude,
                        "longitude":booking.pickup_station.longitude
                    },
                    "dropoff_station":{
                        "id":booking.dropoff_station.id,
                        "address":booking.dropoff_station.name,
                        "latitude":booking.dropoff_station.latitude,
                        "longitude":booking.dropoff_station.longitude
                    },
                }
            else:
                return {}
        else:
            return {}

    def get_city(self, obj):
        return {"id":obj.city.id, "name":obj.city.name} if obj.city else {}


class RouteStationsSerializer(ModelSerializer):
    id = CharField(source='station.id')
    address = CharField(source='station.name')
    latitude = CharField(source='station.latitude')
    longitude = CharField(source='station.longitude')
    
    class Meta:
        model = RoutesStations
        fields = ('id', 'address', 'latitude', 'longitude')


class RidesDatetimeSerializer(ModelSerializer):
    start_datetime = SerializerMethodField(read_only = True)
    end_datetime = SerializerMethodField(read_only = True)
    company_logo = SerializerMethodField(read_only = True)
    pickup_station = SerializerMethodField(read_only = True)
    dropoff_station = SerializerMethodField(read_only = True)
    ride_price = SerializerMethodField(read_only = True)
    currency = CharField(source='route.city.country.currency.symbol')
    bus_details = SerializerMethodField(read_only = True)

    class Meta:
        model = Rides
        fields = ('id','start_datetime','end_datetime','company_logo','pickup_station','dropoff_station','ride_price','currency','seats_left','ride_status','max_seats_per_person','bus_details')

    def get_bus_details(self,obj):
        return {
            "is_ac":obj.assigned_bus.is_ac,
            "is_ev":obj.assigned_bus.is_ev,
            "is_regular":obj.assigned_bus.is_regular,
            "plate_number":obj.assigned_bus.plate_number
        } if obj.assigned_bus else {}

    def get_pickup_station(self, obj):
        pickup_station = self.context.get('pickup_station')
        return {"id":pickup_station.id,"address":pickup_station.name}

    def get_dropoff_station(self, obj):
        dropoff_station = self.context.get('dropoff_station')
        return {"id":dropoff_station.id,"address":dropoff_station.name}

    def get_company_logo(self, obj):
        request = self.context.get('request')
        try:
            company = Companies.objects.get(id=obj.assigned_captain.company_id)
            return request.build_absolute_uri(company.company_logo.url) if company else ""
        except:
            return ""

    def get_start_datetime(self, obj):
        pickup_station = self.context.get('pickup_station')
        pickup_route_station = RoutesStations.objects.get(route = obj.route,station = pickup_station)
        addon_pickuptime = sum([int(station.time_minutes if station.time_minutes else 0) for station in RoutesStations.objects.filter(route = obj.route, index__in=list(range(1,pickup_route_station.index+1)))])
        return (obj.start_datetime + datetime.timedelta(minutes=addon_pickuptime)).strftime("%Y-%m-%d %H:%M:%S")

    def get_end_datetime(self, obj):
        dropoff_station = self.context.get('dropoff_station')
        dropoff_route_station = RoutesStations.objects.get(route = obj.route,station = dropoff_station)
        addon_dropofftime = sum([int(station.time_minutes if station.time_minutes else 0) for station in RoutesStations.objects.filter(route = obj.route, index__in=list(range(1,dropoff_route_station.index+1)))])
        return (obj.start_datetime + datetime.timedelta(minutes=addon_dropofftime)).strftime("%Y-%m-%d %H:%M:%S")

    def get_ride_price(self, obj):
        pickup_station = RoutesStations.objects.get(route = obj.route,station = self.context.get('pickup_station'))
        dropoff_station = RoutesStations.objects.get(route = obj.route,station = self.context.get('dropoff_station'))
        distance = sum([float(station.distance_km if station.distance_km else 0) for station in RoutesStations.objects.filter(route = obj.route,index__in=list(range(pickup_station.index+1, dropoff_station.index+1)))])
        return round(CalculateScheduleFare(obj.schedule, distance))
        

class BookingsListSerializer(ModelSerializer):
    pickup_station = SerializerMethodField(read_only = True)
    dropoff_station = SerializerMethodField(read_only = True)
    booking_price = SerializerMethodField(read_only = True)
    actual_booking_price = SerializerMethodField(read_only = True)
    bus_details = SerializerMethodField(read_only = True)
    currency = CharField(source='route.city.country.currency.symbol')

    class Meta:
        model = Booking
        fields = ('id','boarding_pass','booking_price','currency','pickup_station','dropoff_station','bus_details','status','ride','actual_booking_price')

    def get_booking_price(self, obj):
        return int(round(obj.booking_price) if obj.booking_price else 0) 

    def get_actual_booking_price(self, obj):
        return int(round(obj.actual_booking_price) if obj.actual_booking_price else 0) 

    def get_pickup_station(self, obj):
        return {"id":obj.pickup_station.id,"address":obj.pickup_station.name}

    def get_dropoff_station(self, obj):
        return {"id":obj.dropoff_station.id,"address":obj.dropoff_station.name}

    def get_bus_details(self, obj):
        return {
            "id":obj.ride.assigned_bus.id,
            "plate_number":obj.ride.assigned_bus.plate_number,
            "is_ac":obj.ride.assigned_bus.is_ac,
            "bus_type":obj.ride.assigned_bus.bus_type.name
        }
        

class ReviewSerializer(ModelSerializer):
    class Meta:
        model = Reviews
        fields = ('review', )


class RatingSerializer(ModelSerializer):
    reviews = ReviewSerializer(read_only=True, many=True)

    class Meta:
        model = Rating
        fields = ('rating','reviews','message')


class OfferSerializer(ModelSerializer):
    class Meta:
        model = OfferCodes
        fields = ('id', 'name', 'code','off_percentage','offer_type','expiry_date','description')


class BookingDetailsSerializer(ModelSerializer):
    pickup_station = SerializerMethodField(read_only = True)
    dropoff_station = SerializerMethodField(read_only = True)
    start_datetime = SerializerMethodField(read_only = True)
    end_datetime = SerializerMethodField(read_only = True)
    captain_details = SerializerMethodField(read_only = True)
    bus_details = SerializerMethodField(read_only = True)
    currency = CharField(source='route.city.country.currency.symbol')
    cancellation_reason = SerializerMethodField(read_only = True)
    rating_reviews = SerializerMethodField(read_only = True)
    cancelled_at = SerializerMethodField(read_only = True)
    promo_used = OfferSerializer(read_only = True)
    is_rated = SerializerMethodField(read_only = True)
    booking_price = SerializerMethodField(read_only = True)
    actual_booking_price = SerializerMethodField(read_only = True)

    class Meta:
        model = Booking
        fields = ('id','boarding_pass','booking_price','actual_booking_price','currency','pickup_station','dropoff_station','start_datetime','end_datetime','seats_booked','captain_details','bus_details','status','rating_reviews','route','cancelled_by','cancelled_at','cancellation_reason','custom_cancellation_reason','overview_polyline','promo_used','ride','is_rated')

    def get_booking_price(self, obj):
        return int(round(obj.booking_price) if obj.booking_price else 0) 

    def get_actual_booking_price(self, obj):
        return int(round(obj.actual_booking_price) if obj.actual_booking_price else 0) 

    def get_cancellation_reason(self, obj):
        return obj.cancellation_reason.title if obj.cancellation_reason else ""

    def get_cancelled_at(self,obj):
        return obj.cancelled_at.strftime("%Y-%m-%d %H:%M:%S") if obj.cancelled_at else ""
        
    def get_start_datetime(self, obj):
        return obj.estimated_pickup_time.strftime("%Y-%m-%d %H:%M:%S")

    def get_end_datetime(self, obj):
        return obj.estimated_dropoff_time.strftime("%Y-%m-%d %H:%M:%S")

    def get_pickup_station(self, obj):
        return {
            "id":obj.pickup_station.id,
            "address":obj.pickup_station.name,
            "latitude":obj.pickup_station.latitude,
            "longitude":obj.pickup_station.longitude
        }

    def get_dropoff_station(self, obj):
        return {
            "id":obj.dropoff_station.id,
            "address":obj.dropoff_station.name,
            "latitude":obj.dropoff_station.latitude,
            "longitude":obj.dropoff_station.longitude
        }

    def get_bus_details(self, obj):
        return {
            "id":obj.ride.assigned_bus.id,
            "plate_number":obj.ride.assigned_bus.plate_number,
            "is_ac":obj.ride.assigned_bus.is_ac,
            "bus_type":obj.ride.assigned_bus.bus_type.name
        }

    def get_captain_details(self, obj):
        request = self.context.get('request')
        captain = Captain.objects.get(id=obj.ride.assigned_captain.id)
        return {
            "id":captain.user.id,
            "full_name":captain.user.full_name,
            "country_code":captain.user.country_code,
            "mobile_no":captain.user.mobile_no,
            "profile_pic":request.build_absolute_uri(captain.user.profile_pic.url) if captain.user.profile_pic else "",
            "rating":captain.user.average_rating,
            "company":captain.company.name
        }

    def get_rating_reviews(self, obj):
        request = self.context.get('request')
        rating = Rating.objects.filter(booking=obj, created_by=request.user).last()
        if rating:
            return RatingSerializer(rating, many=False).data
        else:
            return {}

    def get_is_rated(self, obj):
        request = self.context.get('request')
        return True if Rating.objects.filter(booking=obj, created_by=request.user) else False


class TransactionsSerializer(ModelSerializer):
    created_on = SerializerMethodField(read_only = True)
    currency = CharField(source='currency.symbol')

    class Meta:
        model = Transactions
        fields = ('id', 'transaction_id','amount','currency','transaction_type','booking','created_on')

    def get_created_on(self, obj):
        return obj.created_on.strftime("%Y-%m-%d %H:%M:%S")


class RidesListSerializer(ModelSerializer):
    start_datetime = SerializerMethodField(read_only = True)
    end_datetime = SerializerMethodField(read_only = True)
    pickup_station = SerializerMethodField(read_only = True)
    dropoff_station = SerializerMethodField(read_only = True)

    class Meta:
        model = Rides
        fields = ('id','start_datetime','end_datetime','pickup_station','dropoff_station','ride_status')

    def get_start_datetime(self, obj):
        return obj.start_datetime.strftime("%Y-%m-%d %H:%M:%S")

    def get_end_datetime(self, obj):
        return obj.end_datetime.strftime("%Y-%m-%d %H:%M:%S")

    def get_pickup_station(self, obj):
        return {
            "id":obj.start_ride_station.id,
            "address":obj.start_ride_station.name,
            "latitude":obj.start_ride_station.latitude,
            "longitude":obj.start_ride_station.longitude
        }

    def get_dropoff_station(self, obj):
        return {
            "id":obj.end_ride_station.id,
            "address":obj.end_ride_station.name,
            "latitude":obj.end_ride_station.latitude,
            "longitude":obj.end_ride_station.longitude
        }


class RideDetailsSerializer(ModelSerializer):
    start_datetime = SerializerMethodField(read_only = True)
    end_datetime = SerializerMethodField(read_only = True)
    pickup_station = SerializerMethodField(read_only = True)
    dropoff_station = SerializerMethodField(read_only = True)
    ride_stations = SerializerMethodField(read_only = True)
    boarded_pasengers = SerializerMethodField(read_only = True)
    missed_passengers = SerializerMethodField(read_only = True)
    cash_collection = SerializerMethodField(read_only = True)

    class Meta:
        model = Rides
        fields = ('id','start_datetime','end_datetime','pickup_station','dropoff_station','ride_status','ride_stations','boarded_pasengers','missed_passengers','cash_collection','route')

    def get_start_datetime(self, obj):
        return obj.start_datetime.strftime("%Y-%m-%d %H:%M:%S")

    def get_end_datetime(self, obj):
        return obj.end_datetime.strftime("%Y-%m-%d %H:%M:%S")

    def get_pickup_station(self, obj):
        return {
            "id":obj.start_ride_station.id,
            "address":obj.start_ride_station.name,
            "latitude":obj.start_ride_station.latitude,
            "longitude":obj.start_ride_station.longitude
        }

    def get_dropoff_station(self, obj):
        return {
            "id":obj.end_ride_station.id,
            "address":obj.end_ride_station.name,
            "latitude":obj.end_ride_station.latitude,
            "longitude":obj.end_ride_station.longitude
        }

    def get_ride_stations(self, obj):
        data = []
        for station in RoutesStations.objects.filter(route=obj.route).order_by('index'):
            addon_pickuptime = sum([int(station.time_minutes if station.time_minutes else 0) for station in RoutesStations.objects.filter(route = obj.route, index__in=list(range(1,station.index+1)))])
            data.append({
                "id":station.station.id,
                "address":station.station.name,
                "station_datetime":(obj.start_datetime + datetime.timedelta(minutes=addon_pickuptime)).strftime("%Y-%m-%d %H:%M:%S")
            })
        return data

    def get_boarded_pasengers(self, obj):
        return sum([int(booking.seats_booked if booking.seats_booked else 0) for booking in Booking.objects.filter(ride=obj,is_dropoff=True,status=COMPLETE_BOOKING)])

    def get_missed_passengers(self, obj):
        return sum([int(booking.seats_booked if booking.seats_booked else 0) for booking in Booking.objects.filter(ride=obj, status=MISSED_BOOKING)])

    def get_cash_collection(self, obj):
        return sum([int(booking.booking_price if booking.booking_price else 0) for booking in Booking.objects.filter(ride=obj,is_dropoff=True,status=COMPLETE_BOOKING)])


class ReasonsSerializer(ModelSerializer):

    class Meta:
        model = CancelReason
        fields = ('id','title','type_id')


class CitiesSerializer(ModelSerializer):

    class Meta:
        model = Cities
        fields = ('id', 'name', 'latitude','longitude')


class ReviewTextsSerializer(ModelSerializer):
    class Meta:
        model = ReviewText
        fields = ('review',)


class StationBookingsSerializer(ModelSerializer):
    user_details = SerializerMethodField(read_only = True)
    is_missed = SerializerMethodField(read_only = True)

    class Meta:
        model = Booking
        fields = ('id','boarding_pass','user_details','is_pickup','is_dropoff','is_missed')

    def get_is_missed(self, obj):
        return True if int(obj.status) == int(MISSED_BOOKING) else False

    def get_user_details(self, obj):
        return {
            "full_name":obj.created_by.full_name,
            "country_code":obj.created_by.country_code,
            "mobile_no":obj.created_by.mobile_no,
            "profile_pic":self.context.get('request').build_absolute_uri(obj.created_by.profile_pic.url) if obj.created_by.profile_pic else ""
        }
