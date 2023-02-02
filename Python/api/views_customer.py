import environ
from accounts.utils import *
from .serializer import *
from page.models import *
from .pagination import *
from accounts.models import *
from reviews.models import *
from accounts.helper import *
from captains.models import *
from accounts.constants import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from django.db.models import Q
from .utils import *
import datetime
env = environ.Env()
environ.Env.read_env()


class AvailableRoutesList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        routes_id = Rides.objects.filter(ride_status = SCHEDULED_RIDE).values_list('route_id',flat=True)
        if request.user.city:
            city = Cities.objects.get(id=request.user.city.id)
        else:
            city = Cities.objects.filter(default=True).last()
        routes = Routes.objects.filter(id__in=routes_id).order_by('-created_on')
        if city:
            routes = routes.filter(city = city)
        if request.query_params.get('search'):
            route_ids = RoutesStations.objects.filter(station__address__icontains=request.query_params.get('search')).values_list('route_id',flat=True)
            routes = routes.filter(id__in=route_ids).order_by('-created_on')

        all_routes = []
        for route in routes:
            booking = Booking.objects.filter(created_by=request.user, status=COMPLETE_BOOKING).order_by('updated_on').last() 
            if booking:
                if booking.route_id == route.id:
                    all_routes.append(route)

        other_routes = routes.exclude(id__in=[route.id for route in all_routes])
        [all_routes.append(r) for r in other_routes]
        start, end, meta_data = GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None,routes)
        return Response({
            "data":RoutesListSerializer(all_routes[start : end],many=True,context={"request":request}).data,
            "meta" : meta_data,
            "status": status.HTTP_200_OK
        }, status = status.HTTP_200_OK)


class PickupDropoffStations(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            route = Routes.objects.get(id=request.data.get('route_id'))
        except:
            return Response({"message":"Route matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not(request.data.get('pickup') or request.data.get('dropoff')):
            return Response({"message":"Please select the type of stations","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if int(request.data.get('pickup')) == 1:
            excluded_station = RoutesStations.objects.filter(route = route).order_by("index").last()
            stations = RoutesStations.objects.filter(route = route).exclude(id = excluded_station.id).order_by("index")
        elif int(request.data.get('dropoff')) == 1:
            try:
                pickup_station = Stations.objects.get(id=request.data.get('pickup_station_id'))
            except:
                return Response({"message":"Pickup station matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
            stations_list = list(RoutesStations.objects.filter(route = route).order_by("index").values_list('station_id',flat=True))
            station_ids = stations_list[stations_list.index(pickup_station.id):]
            stations = RoutesStations.objects.filter(station_id__in=station_ids[1:],route = route).order_by("index")        
        start,end,meta_data = GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None, stations)
        data = RouteStationsSerializer(stations[start : end],many=True,context={"request":request}).data
        return Response({"data":data,"meta":meta_data,"status": status.HTTP_200_OK}, status = status.HTTP_200_OK)


class RidesDatesList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        dates_list = [(datetime.datetime.today() + datetime.timedelta(days=x)).strftime("%Y-%m-%d") for x in range(0, 6)]
        return Response({"dates_list":dates_list,"status": status.HTTP_200_OK}, status = status.HTTP_200_OK)


class RidesDateSelection(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            route = Routes.objects.get(id=request.data.get('route_id'))
        except:
            return Response({"message":"Route matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            pickup_station = Stations.objects.get(id=request.data.get('pickup_station_id'))
        except:
            return Response({"message":"Pickup station matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            dropoff_station = Stations.objects.get(id=request.data.get('dropoff_station_id'))
        except:
            return Response({"message":"Dropoff station matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            selected_date = datetime.datetime.strptime(request.data.get('selected_date'), "%Y-%m-%d").date()
        except:
            return Response({"message":"Please select a valid date","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        rides = Rides.objects.filter(start_datetime__date=selected_date, route=route, ride_status=SCHEDULED_RIDE).order_by('start_datetime')
        start, end, meta_data = GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None, rides)
        data = RidesDatetimeSerializer(
            rides[start : end],
            many=True,
            context = {
                "request":request, 
                "pickup_station":pickup_station, 
                "dropoff_station":dropoff_station
            }).data
        has_referral_benefits = True if UserReferralCodeUsed.objects.filter(Q(referrer=request.user,referrer_benefit_recieved=False)|Q(referee=request.user, referee_benefit_recieved=False)) else False
        return Response({
            "date":selected_date,
            "data":data,
            "meta":meta_data,
            "has_referral_benefits":has_referral_benefits,
            "status": status.HTTP_200_OK
        }, status = status.HTTP_200_OK)


class CreateBooking(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            route = Routes.objects.get(id=request.data.get('route_id'))
        except:
            return Response({"message":"Route matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            pickup_station = Stations.objects.get(id=request.data.get('pickup_station_id'))
        except:
            return Response({"message":"Pickup station matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            dropoff_station = Stations.objects.get(id=request.data.get('dropoff_station_id'))
        except:
            return Response({"message":"Dropoff station matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            ride = Rides.objects.get(id=request.data.get('ride_id'))
        except:
            return Response({"message":"Ride matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('payment_method'):
            return Response({"message":"Please select payment method","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('seats'):
            return Response({"message":"Please enter number of seats","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('booking_price'):
            return Response({"message":"Please enter booking price","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if int(request.data.get('seats')) > int(ride.seats_left):
            return Response({"message":"Not enough seats available to book.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            start_datetime = datetime.datetime.strptime(request.data.get('start_datetime'), "%Y-%m-%d %H:%M:%S")
        except:
            return Response({"message":"Please enter valid start datetime","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            end_datetime = datetime.datetime.strptime(request.data.get('end_datetime'), "%Y-%m-%d %H:%M:%S")
        except:
            return Response({"message":"Please enter valid end datetime","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)

        if Booking.objects.filter(Q(estimated_pickup_time__lte = start_datetime, estimated_dropoff_time__gte = start_datetime)|Q(estimated_pickup_time__lte = end_datetime, estimated_dropoff_time__gte = end_datetime), route=ride.route,created_by = request.user,status=BOOKED):
            return Response({"message":"You already have a booking for the selected slot on this route. Kindly select another route or slot.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)

        if request.data.get('promo_used'):
            if not request.data.get('actual_booking_price'):
                return Response({"message":"Please enter booking price","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
            try:
                promo_used = OfferCodes.objects.get(id=request.data.get('promo_used'))
            except:
                return Response({"message":"Invalid Offer Code","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        else:
            promo_used = None
            
        boarding_pass = GenerateBoardingPass(ride)
        booking = Booking.objects.create(
            created_by = request.user,
            route = route,
            status = BOOKED,
            seats_booked = request.data.get('seats'),
            ride = ride,
            booking_price = round(float(request.data.get('booking_price'))),
            actual_booking_price = round(float(request.data.get('actual_booking_price'))) if request.data.get('actual_booking_price') else round(float(request.data.get('booking_price'))),
            payment_method = request.data.get('payment_method'),
            pickup_station = pickup_station,
            dropoff_station = dropoff_station,
            estimated_pickup_time = start_datetime,
            estimated_dropoff_time = end_datetime,
            boarding_pass = boarding_pass
        )
        ride.seats_left = int(ride.seats_left) - int(request.data.get('seats'))
        ride.save()
        GetBookingPolyline(booking,env('GOOGLE_PLACES_KEY'))
        CreateTransaction(request.user, request.user, round(float(request.data.get('booking_price'))), booking, AMOUNT_DEDUCTED,route.city.country.currency)
        if promo_used:
            booking.promo_used = promo_used
            booking.save()
            try:
                code_used = OfferCodeUsed.objects.get(user=request.user, code = promo_used)
                code_used.used_count += 1 
                code_used.save()
            except:
                OfferCodeUsed.objects.create(user=request.user, code = promo_used, used_count=1)
            if promo_used.offer_type == OFFER_REFERRAL_REWARD_TYPE:
                UserReferralCodeUsed.objects.filter(referrer=request.user,referrer_benefit_recieved=False).update(referrer_benefit_recieved=True)
                UserReferralCodeUsed.objects.filter(referee=request.user,referee_benefit_recieved=False).update(referee_benefit_recieved=True)
        message = "Your Ticket has successfully booked for "+str(route.city.country.currency.symbol) + str(round(float(request.data.get('booking_price'))))
        data = BookingDetailsSerializer(booking,many=False,context={"request":request}).data
        return Response({"message":message,"data":data,"status": status.HTTP_200_OK}, status = status.HTTP_200_OK)


class BookingsList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        if not(request.data.get('upcoming') or request.data.get('completed')):
            return Response({"message":"Please select the type of bookings","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        bookings = Booking.objects.filter(created_by=request.user)
        if int(request.data.get('upcoming')) == 1:
            bookings = bookings.filter(status=BOOKED).order_by('-estimated_pickup_time')
        elif int(request.data.get('completed')) == 1:
            bookings = bookings.filter(Q(status=COMPLETE_BOOKING)|Q(status=CANCELLED_BOOKING)|Q(status=MISSED_BOOKING)).order_by('-updated_on')
        start,end,meta_data = GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None, bookings)
        data = BookingsListSerializer(bookings[start : end],many=True,context={"request":request}).data
        return Response({"data":data,"meta":meta_data,"status": status.HTTP_200_OK}, status = status.HTTP_200_OK)


class BookingDetails(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            booking = Booking.objects.get(id=request.data.get('booking_id'))
        except:
            return Response({"message":"Booking matching query doesnot exist","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        data = BookingDetailsSerializer(booking,many=False,context={"request":request}).data
        return Response({"data":data,"status": status.HTTP_200_OK}, status = status.HTTP_200_OK)


class CancelBooking(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            booking = Booking.objects.get(id=request.data.get('booking_id'))
        except:
            return Response({"message":"Booking matching query doesnot exist","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not(request.data.get('reason_id') or request.data.get('reason')):
            return Response({"message":"Please enter or select a reason for cancellation.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if request.data.get('reason_id'):
            try:
                reason = CancelReason.objects.get(id = request.data.get('reason_id'))
            except:
                return Response({"message":"Please select a valid reason","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        ride = Rides.objects.get(id=booking.ride.id)
        if ride.ride_status == SCHEDULED_RIDE:
            if booking.status == BOOKED:
                booking.status = CANCELLED_BOOKING
                booking.cancelled_by = request.user
                booking.cancellation_reason = reason if request.data.get('reason_id') else None
                booking.custom_cancellation_reason = request.data.get('reason') if request.data.get('reason') else None
                booking.cancelled_at = datetime.datetime.now()
                booking.save()
                ride.seats_left = int(ride.seats_left if ride.seats_left else 0) + int(booking.seats_booked if booking.seats_booked else 0)
                ride.save()
                CreateTransaction(request.user, request.user, booking.booking_price, booking, AMOUNT_RECIEVED, booking.route.city.country.currency)
                message = "Booking Cancelled Successfully!"
            else:
                message = "Sorry! We are unable to cancel your booking at the moment!"
        else:
            message = "Sorry! We are unable to cancel your booking at the moment!"
        return Response({"message":message,"status": status.HTTP_200_OK}, status = status.HTTP_200_OK)


class CustomerTransactions(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        wallet = UserWallet.objects.get(user=request.user)
        transactions = Transactions.objects.filter(created_for=request.user)

        ## Filters
        if int(request.data.get('weekly')) == 0 and int(request.data.get('monthly')) == 0 and int(request.data.get('yearly')) == 0:
            if request.data.get('selected_date'):
                transactions = transactions.filter(created_on__date=request.data.get('selected_date'))
        if int(request.data.get('weekly')) == 1:
            transactions = transactions.filter(created_on__date__in=GetWeekDates()) 
        if int(request.data.get('monthly')) == 1:
            transactions = transactions.filter(created_on__month=datetime.datetime.now().month) 
        if int(request.data.get('yearly')) == 1:
            transactions = transactions.filter(created_on__year=datetime.datetime.now().year) 

        start,end,meta_data = GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None, transactions)
        data = TransactionsSerializer(transactions[start : end],many=True,context={"request":request}).data
        return Response({"wallet_amount":wallet.amount,"data":data,"meta":meta_data,"status": status.HTTP_200_OK}, status = status.HTTP_200_OK)


class ReviewTextsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        # review_texts = ReviewText.objects.all()
        # data = ReviewTextsSerializer(review_texts,many=True,context={"request":request}).data
        # return Response({"data":data,"status": status.HTTP_200_OK}, status = status.HTTP_200_OK)
        data = [review_text.review for review_text in ReviewText.objects.all()]
        return Response({"data":data,"status": status.HTTP_200_OK}, status = status.HTTP_200_OK)


class RateRide(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            booking = Booking.objects.get(id=request.data.get('booking_id'))
        except:
            return Response({"message":"Booking matching query doesnot exist","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('rating'):
            return Response({"message":"Please enter rating for trip","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('reviews_count'):
            return Response({"message":"Please enter reviews count","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)

        if Rating.objects.filter(booking=booking, created_by=request.user):
            return Response({"message":"You have already rated this trip.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        else:
            user = User.objects.get(id=booking.ride.assigned_captain.user.id)
            rating = Rating.objects.create(
                rating = request.data.get('rating'),
                created_for = user,
                booking = booking,
                created_by = request.user,
                message = request.data.get('message') if request.data.get('message') else ""
            )
            for i in range(0,int(request.data.get("reviews_count",'0'))+1):
                if request.data.get("review{}".format(i),None):
                    rating.reviews.add(Reviews.objects.create(review=request.data.get("review{}".format(i))))
            user.average_rating = round(float(sum([float(i.rating if i.rating else 0) for i in Rating.objects.filter(created_for = user)])/Rating.objects.filter(created_for = user).count()),2)
            user.save()
            return Response({"message":"Trip Rated Successfully!","status": status.HTTP_200_OK}, status = status.HTTP_200_OK)

        
class CancellationReasonsList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        if not request.data.get('type_id'):
            return Response({"message":"Please enter reason type","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)

        reasons = CancelReason.objects.filter(type_id=request.data.get('type_id'),is_active=True).order_by('-created_on')
        start,end,meta_data = GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None, reasons)
        data = ReasonsSerializer(reasons[start : end],many=True,context={"request":request}).data
        return Response({"data":data,"meta":meta_data,"status": status.HTTP_200_OK}, status = status.HTTP_200_OK)


class SearchRideDatetime(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        if not request.data.get('pickup_latitude') and not request.data.get('pickup_longitude') and not request.data.get('dropoff_latitude') and not request.data.get('dropoff_longitude'):
            return Response({"message":"Please select the pickup and dropoff location","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)   
        
        pickup_station_ids = [pickup_station.id for pickup_station in Stations.objects.raw('''SELECT id, ( 6357 * acos( cos( radians( {0} ) ) * cos( radians(latitude) ) * cos( radians(longitude) - radians( {1} ) ) + sin( radians( {0} ) ) * sin( radians(latitude) ) ) ) AS distance FROM stations{2} Having  distance < 3 ORDER BY distance;'''.format(request.data.get('pickup_latitude'),request.data.get('pickup_longitude'),''))]
        
        dropoff_station_ids = [dropoff_station.id for dropoff_station in Stations.objects.raw('''SELECT id, ( 6357 * acos( cos( radians( {0} ) ) * cos( radians(latitude) ) * cos( radians(longitude) - radians( {1} ) ) + sin( radians( {0} ) ) * sin( radians(latitude) ) ) ) AS distance FROM stations{2} Having  distance < 3 ORDER BY distance;'''.format(request.data.get('dropoff_latitude'),request.data.get('dropoff_longitude'),''))]
        
        ## Available Routes
        station_combination = RouteStationsCombination.objects.filter(from_station_id__in=pickup_station_ids, to_station_id__in=dropoff_station_ids).values_list('route_id',flat=True)
        routes = Routes.objects.filter(id__in=station_combination)

        ## Checks For the rides in the Routes
        ride_route_id = Rides.objects.filter(ride_status = SCHEDULED_RIDE).values_list('route_id',flat=True)
        routes = routes.filter(id__in = ride_route_id)

        ## Search History
        try:
            search = UserRideSearch.objects.get(
                user = request.user,
                pickup_latitude = request.data.get('pickup_latitude'),
                pickup_longitude = request.data.get('pickup_longitude'),
                dropoff_latitude = request.data.get('dropoff_latitude'),
                dropoff_longitude = request.data.get('dropoff_longitude'),
            )
            search.pickup_address = request.data.get('pickup_address') if request.data.get('pickup_address') else ""
            search.dropoff_address = request.data.get('dropoff_address') if request.data.get('dropoff_address') else ""
            search.is_ride_available = True if routes else False
            search.is_pickup_available = True if pickup_station_ids else False
            search.is_dropoff_available = True if dropoff_station_ids else False
            search.search_count += 1
            search.save()
        except:
            UserRideSearch.objects.create(
                user = request.user,
                pickup_latitude = request.data.get('pickup_latitude'),
                pickup_longitude = request.data.get('pickup_longitude'),
                pickup_address = request.data.get('pickup_address') if request.data.get('pickup_address') else "",
                dropoff_latitude = request.data.get('dropoff_latitude'),
                dropoff_longitude = request.data.get('dropoff_longitude'),
                dropoff_address = request.data.get('dropoff_address') if request.data.get('dropoff_address') else "",
                is_ride_available = True if routes else False,
                is_pickup_available = True if pickup_station_ids else False,
                is_dropoff_available = True if dropoff_station_ids else False
            )

        start, end, meta_data = GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None,routes)
        return Response({
            "data":RoutesListSerializer(routes[start : end],many=True,context={"request":request}).data,
            "meta" : meta_data,
            "status": status.HTTP_200_OK
        }, status = status.HTTP_200_OK)
            

class CustomerOffersList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            route = Routes.objects.get(id=request.data.get('route_id'))
        except:
            return Response({"message":"Route matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        offer_ids = []
        code_ids = OfferCodes.routes.through.objects.filter(routes=route).values_list('offercodes_id',flat=True)
        route_promo = OfferCodes.objects.filter(id__in=code_ids,promo_status=ACTIVE_PROMO,offer_type=OFFER_PROMO_TYPE).last()
        if route_promo:
            code_used = OfferCodeUsed.objects.filter(code=route_promo,user=request.user).last()
            if code_used:
                if code_used.used_count >= route_promo.max_usage_per_person:
                   route_promo = None 
        if route_promo:
            offer_ids.append(route_promo.id)
        if UserReferralCodeUsed.objects.filter(Q(referrer=request.user,referrer_benefit_recieved=False)|Q(referee=request.user, referee_benefit_recieved=False)):
            referral_promo = OfferCodes.objects.filter(promo_status=ACTIVE_PROMO,offer_type=OFFER_REFERRAL_REWARD_TYPE).last()
        else:
            referral_promo = None
        if referral_promo:
            offer_ids.append(referral_promo.id)
        data = OfferSerializer(OfferCodes.objects.filter(id__in=offer_ids), many=True, context = {"request":request}).data   
        return Response({"data":data,"status": status.HTTP_200_OK}, status = status.HTTP_200_OK)


class GetRideLocation(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            ride = Rides.objects.get(id=request.data.get('ride_id'))
        except:
            return Response({"message":"Ride matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        return Response({"data":{
            "ride_id":ride.id,
            "latitude":ride.latitude,
            "longitude":ride.longitude
        },"status": status.HTTP_200_OK}, status = status.HTTP_200_OK)
        
 
        