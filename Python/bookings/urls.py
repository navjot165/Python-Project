from django.contrib import admin
from .views import *
from django.urls import re_path

admin.autodiscover()
app_name = 'bookings'


urlpatterns = [

    ## Bookings
    re_path(r'bookings-list/$',BookingsList,name="bookings_list"),
    re_path(r'view-booking/(?P<id>[-\w]+)/$',ViewBooking,name="view_booking"),

    ## Bookings
    re_path(r'cancellation-reasons/$',CancellationReasons,name="cancellation_reasons"),
    re_path(r'add-reason/$',AddReason,name="add_reason"),
    re_path(r'activate-deactivate-reason/$',ActivateDeactivateReason,name="activate_deactivate_reason"),
    re_path(r'delete-reason/(?P<id>[-\w]+)/$',DeleteReason,name="delete_reason"),

]