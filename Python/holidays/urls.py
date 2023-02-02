from django.contrib import admin
from .views import *
from django.urls import re_path


admin.autodiscover()
app_name = 'holidays'


urlpatterns = [

    ## Categories
    re_path(r'categories-list/$',RouteCategoriesList,name="route_categories_list"),
    re_path(r'add-category/$',AddRouteCategory,name="add_route_category"),
    re_path(r'view-category/(?P<id>[-\w]+)/$',ViewRouteCategory,name="view_route_category"),
    re_path(r'delete-category/(?P<id>[-\w]+)/$',DeleteRouteCategory,name="delete_route_category"),
    re_path(r'edit-category/(?P<id>[-\w]+)/$',EditRouteCategory,name="edit_route_category"),

    ## Holidays
    re_path(r'holidays-list/$',HolidaysList,name="holidays_list"),
    re_path(r'add-holiday/$',AddHoliday,name="add_holiday"),
    re_path(r'view-holiday/(?P<id>[-\w]+)/$',ViewHoliday,name="view_holiday"),
    re_path(r'delete-holiday/(?P<id>[-\w]+)/$',DeleteHoliday,name="delete_holiday"),
    re_path(r'edit-holiday/(?P<id>[-\w]+)/$',EditHoliday,name="edit_holiday"),
]
