from django.contrib import admin
from .views import *
from django.urls import re_path


admin.autodiscover()
app_name = 'charging_sites'


urlpatterns = [
    re_path(r'charging-site-list/$', ChargingSitesList, name="charging_sites_list"),
    re_path(r'add-charging-site/$', AddChargingSite, name="add_charging_site"),
    re_path(r'check-time-validations/$', CheckTimeValidations, name="check_time_validations"),
    re_path(r'view-charging-site/(?P<id>[-\w]+)/$', ViewChargingSite, name="view_charging_site"),
    re_path(r'delete-charging-site/(?P<id>[-\w]+)/$', DeleteChargingSite, name="delete_charging_site"),
    re_path(r'edit-charging-site/(?P<id>[-\w]+)/$', EditChargingSite, name="edit_charging_site"),
]