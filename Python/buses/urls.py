from django.contrib import admin
from .views import *
from django.urls import re_path


admin.autodiscover()
app_name = 'buses'


urlpatterns = [
    
    # Bus Types
    re_path(r'^bus-types-list/$', BusTypesList, name='bus_types'),
    re_path(r'^add-bus-type/$', AddBusType, name='add_bus_type'),
    re_path(r'^view-bus-type/(?P<id>[-\w]+)/$', ViewBusType, name='view_bus_type'),
    re_path(r'^delete-bus-type/(?P<id>[-\w]+)/$', DeleteBusType, name='delete_bus_type'),
    re_path(r'^edit-bus-type/(?P<id>[-\w]+)/$', EditBusType, name='edit_bus_type'),

    # Buses
    re_path(r'^buses-list/$', BusesList, name='buses_list'),
    re_path(r'^add-bus/$', AddBus, name='add_bus'),
    re_path(r'^activate-deactivate-bus/$', ActivateDeactivateBus, name='activate_deactivate_bus'),
    re_path(r'^bus-validations/$', BusValidations, name='bus_validations'),
    re_path(r'^view-bus/(?P<id>[-\w]+)/$', ViewBus, name='view_bus'),
    re_path(r'^edit-bus/(?P<id>[-\w]+)/$', EditBus, name='edit_bus'),
    re_path(r'^delete-bus/(?P<id>[-\w]+)/$', DeleteBus, name='delete_bus'),

]