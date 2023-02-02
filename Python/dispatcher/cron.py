from holidays.models import *
from cities.models import *
from routes.models import *
from .models import *
from .helper import *
from .views import CreateDispatchedRides
import logging
db_logger = logging.getLogger('db')


def dispatch_rides():
    try:
        active_dispatches = Dispatcher.objects.filter(is_active=True) 
        if active_dispatches:
            for dispatch in active_dispatches:
                selected_categories = Dispatcher.categories.through.objects.filter(dispatcher_id=dispatch.id).values_list('category_id',flat=True)
                selected_cities = Dispatcher.cities.through.objects.filter(dispatcher_id=dispatch.id).values_list('cities_id',flat=True)
                routes = Routes.objects.filter(Q(city_id__in=selected_cities)|Q(category_id__in=selected_categories))
                schedules = Schedules.objects.filter(route_id__in=routes.values_list('id',flat=True),is_active=True)
                created_rides_id, dispatch_state = CreateDispatchedRides(dispatch,schedules)
                dispatch.total_runs += 1
                dispatch.save()
                dispatch_report = DispatcherReports.objects.create(
                    dispatcher=dispatch, 
                    rides_dispatched=len(created_rides_id),
                    status = DISPATCH_SUCCESS if dispatch_state else False,
                    dispatch_type = MANUAL
                )
                [dispatch_report.rides.add(Rides.objects.get(id=ride_id)) for ride_id in created_rides_id]
    except Exception as e:
        db_logger.exception(e)