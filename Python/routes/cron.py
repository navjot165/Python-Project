from accounts.models import *
from accounts.constants import *
from bookings.models import *
from .models import *
from offers.models import *
import datetime
import logging
db_logger = logging.getLogger('db')


def cancel_rides_cronjob():
    try:
        for ride in Rides.objects.filter(Q(ride_status=SCHEDULED_RIDE)|Q(ride_status=INPROGRESS_RIDE)|Q(ride_status=ARRIVED_AT_STATION)|Q(ride_status=STOPPED_RIDE)):
            if ride.ride_status == SCHEDULED_RIDE:
                if ride.start_datetime <= datetime.datetime.now() + datetime.timedelta(minutes=30+int(ride.schedule.arrival_allowance)):
                    ride.ride_status = CANCELLED_RIDE
                    ride.save()
                    Booking.objects.filter(ride=ride, status=BOOKED).update(status=CANCELLED_BOOKING)
            else:
                if ride.end_datetime <= datetime.datetime.now() + datetime.timedelta(minutes=30+int(ride.schedule.departure_allowance)):
                    ride.ride_status = CANCELLED_RIDE
                    ride.save()
                    Booking.objects.filter(ride=ride, status=BOOKED).update(status=CANCELLED_BOOKING)
    except Exception as exception:
        db_logger.exception(exception)


def expire_promocodes():
    OfferCodes.objects.filter(offer_type=OFFER_PROMO_TYPE,expiry_date__lte = datetime.datetime.now().date()).update(promo_status=EXPIRED_PROMO)