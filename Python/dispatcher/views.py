import logging
from accounts.decorators import *
from accounts.helper import *
from accounts.utils import *
from holidays.models import *
from cities.models import *
from routes.models import *
from frontend.views import *
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import *
import datetime
from .helper import *
db_logger = logging.getLogger('db')


@admins_only
@check_permissions('dispatcher.dispatcher_list')
def DispatchesList(request):
    dispatches = Dispatcher.objects.all().order_by('-created_on')
    if request.GET.get('no_of_days'):
        dispatches = dispatches.filter(no_of_days = request.GET.get('no_of_days'))
    if request.GET.get('allow_manual_dispatch'):
        dispatches = dispatches.filter(allow_manual_dispatch = request.GET.get('allow_manual_dispatch'))
    if request.GET.get('total_runs'):
        dispatches = dispatches.filter(total_runs = request.GET.get('total_runs'))
    if request.GET.get('is_active'):
        dispatches = dispatches.filter(is_active = request.GET.get('is_active'))
    if request.GET.get('run_current_day'):
        dispatches = dispatches.filter(run_current_day = request.GET.get('run_current_day'))
    if request.GET.get('created_on'):
        dispatches = dispatches.filter(created_on__date = request.GET.get('created_on'))
    if request.GET.get('categories'):
        dispatches = dispatches.filter(categories__name__icontains = request.GET.get('categories'))
    if request.GET.get('cities'):
        dispatches = dispatches.filter(cities__name__icontains = request.GET.get('cities'))
    if request.GET and not dispatches:
        messages.error(request, 'No Data Found')
    return render(request, 'dispatcher/dispatches-list.html',{
        "head_title":"Dispatcher Management",
        "dispatches":get_pagination(request, dispatches),
        "no_of_days": request.GET.get('no_of_days') if request.GET.get('no_of_days') else "",
        "allow_manual_dispatch": request.GET.get('allow_manual_dispatch') if request.GET.get('allow_manual_dispatch') else "",
        "run_current_day": request.GET.get('run_current_day') if request.GET.get('run_current_day') else "",
        "categories": request.GET.get('categories') if request.GET.get('categories') else "",
        "cities": request.GET.get('cities') if request.GET.get('cities') else "",
        "is_active": request.GET.get('is_active') if request.GET.get('is_active') else "",
        "created_on": request.GET.get('created_on') if request.GET.get('created_on') else "",
        "total_runs": request.GET.get('total_runs') if request.GET.get('total_runs') else ""
    })


@admins_only
@check_permissions('dispatcher.add_dispatch')
def AddDispatch(request):
    if request.method == 'POST':
        dispatch = Dispatcher.objects.create(
            no_of_days = request.POST.get('no_of_days'),
            allow_manual_dispatch = request.POST.get('allow_manual_dispatch'),
            run_current_day = request.POST.get('run_current_day'),
            is_active = False if Dispatcher.objects.filter(is_active=True,categories__id__in=request.POST.getlist('categories'), cities__id__in=request.POST.getlist('cities')) else True
        )
        [dispatch.categories.add(Category.objects.get(id=category)) for category in request.POST.getlist('categories')]
        [dispatch.cities.add(Cities.objects.get(id=city)) for city in request.POST.getlist('cities')]
        messages.success(request, "Dispatch Added Successfully!")
        return redirect('dispatcher:view_dispatch',id=dispatch.id)
    return render(request, 'dispatcher/add-dispatch.html',{
        "head_title":"Dispatcher Management",
        "categories":Category.objects.all().order_by('-created_on'),
        "cities":Cities.objects.all().order_by('-created_on'),
    })


@admins_only
@check_permissions('dispatcher.view_dispatch')
def ViewDispatch(request, id):
    dispatch = Dispatcher.objects.get(id=id)
    dispatch_reports = DispatcherReports.objects.filter(dispatcher=dispatch).order_by('-dispatched_on')
    return render(request, 'dispatcher/view-dispatch.html',{
        "head_title":"Dispatcher Management",
        "dispatch":dispatch,
        "dispatch_reports":get_pagination(request, dispatch_reports)
    })


@admins_only
@check_permissions('dispatcher.delete_dispatch')
def DeleteDispatch(request, id):
    Dispatcher.objects.get(id=id).delete()
    messages.success(request, 'Dispatch Deleted Successfully!')
    return redirect('dispatcher:dispatches_list')


@admins_only
@check_permissions('dispatcher.edit_dispatch')
def EditDispatch(request, id):
    dispatch = Dispatcher.objects.get(id=id)
    selected_categories = Dispatcher.categories.through.objects.filter(dispatcher_id=id).values_list('category_id',flat=True)
    selected_cities = Dispatcher.cities.through.objects.filter(dispatcher_id=id).values_list('cities_id',flat=True)
    if request.method == 'POST':
        dispatch.no_of_days = request.POST.get('no_of_days')
        dispatch.allow_manual_dispatch = request.POST.get('allow_manual_dispatch')
        dispatch.run_current_day = request.POST.get('run_current_day')
        Dispatcher.cities.through.objects.filter(dispatcher_id=id).delete()
        Dispatcher.categories.through.objects.filter(dispatcher_id=id).delete()
        [dispatch.categories.add(Category.objects.get(id=category)) for category in request.POST.getlist('categories')]
        [dispatch.cities.add(Cities.objects.get(id=city)) for city in request.POST.getlist('cities')]
        dispatch.save()
        messages.success(request, "Dispatch Updated Successfully!")
        return redirect('dispatcher:view_dispatch',id=dispatch.id)
    return render(request, 'dispatcher/edit-dispatch.html',{
        "head_title":"Dispatcher Management",
        "dispatch":dispatch,
        "categories":Category.objects.all().exclude(id__in=selected_categories),
        "cities":Cities.objects.all().exclude(id__in=selected_cities),
        "selected_categories":Category.objects.filter(id__in=selected_categories),
        "selected_cities":Cities.objects.filter(id__in=selected_cities)
    })


@admins_only
@check_permissions('dispatcher.activate_deactivate_dispatch')
def ActivateDeactivateDispatch(request):
    if request.method == 'POST':
        dispatch = Dispatcher.objects.get(id=request.POST.get('dispatch_id'))
        if dispatch.is_active:
            dispatch.is_active = False
            messages.success(request, 'Dispatch Deactivated Successfully!')
        else:
            Dispatcher.objects.filter(is_active=True).exclude(id=dispatch.id).update(is_active=False)
            dispatch.is_active = True
            messages.success(request, 'Dispatch Activated Successfully!')
        dispatch.save()
        return redirect('dispatcher:view_dispatch',id=dispatch.id) 


@admins_only
@check_permissions('dispatcher.dispatch_manual_rides')
def DispatchManualRides(request, id):
    dispatch = Dispatcher.objects.get(id=id)
    selected_categories = Dispatcher.categories.through.objects.filter(dispatcher_id=id).values_list('category_id',flat=True)
    selected_cities = Dispatcher.cities.through.objects.filter(dispatcher_id=id).values_list('cities_id',flat=True)
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
    messages.success(request, 'Rides Dispatched Successfully!')
    return redirect('dispatcher:view_dispatch',id=dispatch.id) 


def CreateDispatchedRides(dispatch,schedules):
    rides_created = []
    try:
        for schedule in schedules:
            schedules_week_days = GetScheduleWeekDays(schedule)
            dates_list = []
            if dispatch.run_current_day:
                for x in range(0, int(dispatch.no_of_days)):
                    next_date = (datetime.datetime.today() + datetime.timedelta(days=x))
                    dates_list.append(next_date.date()) if next_date.weekday() in schedules_week_days else ""
            else:
                for x in range(0, int(dispatch.no_of_days)):
                    next_date = ((datetime.datetime.today() + datetime.timedelta(days=1)) + datetime.timedelta(days=x))
                    dates_list.append(next_date.date()) if next_date.weekday() in schedules_week_days else ""
            [dates_list.remove(holiday.holiday_date) if holiday.holiday_date in dates_list else "" for holiday in Holidays.objects.filter(holiday_date__year=datetime.datetime.now().year)]
            if dates_list:
                for selected_date in dates_list:
                    start_datetime = datetime.datetime.combine(selected_date, schedule.start_time)
                    if dispatch.run_current_day:
                        if start_datetime >= datetime.datetime.now():
                            create_ride = True
                        else:
                            create_ride = False
                    else:
                        create_ride = True
                    if create_ride:
                        end_datetime = datetime.timedelta(minutes=int(schedule.route.total_time_minutes))+start_datetime
                        if not Rides.objects.filter(Q(start_datetime__lte = start_datetime, end_datetime__gte = start_datetime)|Q(start_datetime__lte = end_datetime, end_datetime__gte = end_datetime), route=schedule.route, schedule=schedule, assigned_bus=schedule.assigned_bus, ride_status=SCHEDULED_RIDE):
                            ride = Rides.objects.create(
                                start_datetime = start_datetime,
                                end_datetime = end_datetime, 
                                dispatch_type = AUTOMATIC,
                                schedule = schedule,
                                route = schedule.route,
                                ride_price = schedule.schedule_price,
                                assigned_captain = schedule.assigned_captain,
                                is_manual = False,
                                is_emergency = False,
                                is_confirmed = True,
                                start_ride_station = schedule.start_station,
                                end_ride_station = schedule.end_station,
                                price_config = CUSTOM_PRICE if schedule.price_overrided else CATEGORY_PRICE,
                                assigned_bus = schedule.assigned_bus,
                                timezone = schedule.timezone,
                                total_seats = schedule.assigned_bus.bus_type.seat_count,
                                seats_left = schedule.assigned_bus.bus_type.seat_count,
                                category_type = schedule.category_type,
                                flags = schedule.flags,
                                max_seats_per_person = schedule.max_seats_per_person,
                                arrival_allowance = schedule.arrival_allowance,
                                departure_allowance = schedule.departure_allowance,
                            )
                            rides_created.append(ride.id)
        dispatch_state = True
    except Exception as e:
        db_logger.exception(e)
        dispatch_state = False
    return rides_created, dispatch_state