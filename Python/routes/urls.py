from django.contrib import admin
from .views import *
from .views_schedules import *
from .views_rides import *
from .views_ride_passengers import *
from django.urls import re_path


admin.autodiscover()
app_name = 'routes'


urlpatterns = [
    
    ## Stations
    re_path(r'stations-list/$',StationsListView,name="stations_list"),
    re_path(r'add-station/$',AddStationView,name="add_station"),
    re_path(r'view-station/(?P<id>[-\w]+)/$',ViewStation,name="view_station"),
    re_path(r'delete-station/(?P<id>[-\w]+)/$',DeleteStation,name="delete_station"),

    ## Routes
    re_path(r'routes-list/$',RoutesListView,name="routes_list"),
    re_path(r'add-route-details/$',AddRouteDetails,name="add_route_details"),
    re_path(r'add-route-stations/(?P<id>[-\w]+)/$',AddRouteStations,name="add_route_stations"),
    re_path(r'view-route/(?P<id>[-\w]+)/$',ViewRoute,name="view_route"),
    re_path(r'delete-route/(?P<id>[-\w]+)/$',DeleteRoute,name="delete_route"),
    re_path(r'activate-inactivate-route/$',ActivateInactivateRoute,name="activate_inactivate_route"),
    re_path(r'edit-route-details/(?P<id>[-\w]+)/$',EditRouteDetails,name="edit_route_details"),
    re_path(r'edit-route-stations/(?P<id>[-\w]+)/$',EditRouteStations,name="edit_route_stations"),

    ## Schedules
    re_path(r'schedules-list/$',SchedulesList,name="schedules_list"),
    re_path(r'add-schedule/$',AddSchedule,name="add_schedule"),
    re_path(r'schedule-vaidations/$',ScheduleValidations,name="schedule_vaidations"),
    re_path(r'get-price-configurations/$',GetPriceConfigurations,name="get_price_configurations"),
    re_path(r'view-schedules/(?P<id>[-\w]+)/$',ViewSchedule,name="view_schedule"),
    re_path(r'delete-schedule/(?P<id>[-\w]+)/$',DeleteSchedule,name="delete_schedule"),
    re_path(r'edit-schedule/(?P<id>[-\w]+)/$',EditSchedule,name="edit_schedule"),
    re_path(r'activate-inactivate-schedule/$',ActivateInactivateSchedule,name="activate_inactivate_schedule"),

    ## Rides
    re_path(r'rides-list/$',RidesList,name="rides_list"),
    re_path(r'add-ride/$',AddRide,name="add_ride"),
    re_path(r'get-route-schedules/$',GetRouteSchedules,name="get_route_schedules"),
    re_path(r'get-schedule-days/$',GetScheduleDays,name="get_schedule_days"),
    re_path(r'get-assigned-captains/$',GetAssignedCaptains,name="get_assigned_captains"),
    re_path(r'view-ride/(?P<id>[-\w]+)/$',ViewRide,name="view_ride"),
    re_path(r'delete-ride/(?P<id>[-\w]+)/$',DeleteRide,name="delete_ride"),
    re_path(r'edit-ride/(?P<id>[-\w]+)/$',EditRide,name="edit_ride"),
    re_path(r'cancel-ride/(?P<id>[-\w]+)/$',CancelRide,name="cancel_ride"),

    ## Rides Search History
    re_path(r'rides-search-history/$',RidesSearchHistoryList,name="rides_search_history"),
    re_path(r'clear-search-history/$',ClearSearchHistory,name="clear_search_history"),
    re_path(r'view-search-history/(?P<id>[-\w]+)/$',ViewSearchHistory,name="view_search_history"),
    re_path(r'delete-search-history/(?P<id>[-\w]+)/$',DeleteSearchHistory,name="delete_search_history"),


    ## Ride Passengers
    re_path(r'rides-passengers-list/(?P<id>[-\w]+)/$',RidePassengersList,name="ride_passengers"),
    re_path(r'start-ride/(?P<id>[-\w]+)/$',StartRideView,name="start_ride"),
    re_path(r'end-ride/(?P<id>[-\w]+)/$',EndRideView,name="end_ride"),
    re_path(r'change-ride-passengers-status/(?P<ride_id>[-\w]+)/(?P<booking_id>[-\w]+)/$',ChangeRidePassengersStatus,name="change_ride_passenger_status"),
    
]