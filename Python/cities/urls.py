from django.contrib import admin
from .views import *
from django.urls import re_path


admin.autodiscover()
app_name = 'cities'


urlpatterns = [

    ## Currencies
    re_path(r'currencies-list/$',CurrenciesList,name="currencies_list"),
    re_path(r'delete-currency/(?P<id>[-\w]+)/$',DeleteCurrency,name="delete_currency"),

    ## Countries
    re_path(r'countries-list/$',CountriesList,name="countries_list"),
    re_path(r'add-country/$',AddCountry,name="add_country"),
    re_path(r'^delete-country/(?P<id>[-\w]+)/$', DeleteCountry, name='delete_country'),
    re_path(r'^view-country/(?P<id>[-\w]+)/$', ViewCountry, name='view_country'),
    re_path(r'^edit-country/(?P<id>[-\w]+)/$', EditCountry, name='edit_country'),

    ## Cities
    re_path(r'cities-list/$',CitiesList,name="cities_list"),
    re_path(r'add-city/$',AddCity,name="add_city"),
    re_path(r'^delete-city/(?P<id>[-\w]+)/$', DeleteCity, name='delete_city'),
    re_path(r'^view-city/(?P<id>[-\w]+)/$', ViewCity, name='view_city'),
    re_path(r'^edit-city/(?P<id>[-\w]+)/$', EditCity, name='edit_city'),
    re_path(r'^edit-country/$', EditCountry, name='edit_country'),

    ## Districts
    re_path(r'districts-list/$',DistrictsList,name="districts_list"),
    re_path(r'add-district/$',AddDistrict,name="add_district"),
    re_path(r'^delete-district/(?P<id>[-\w]+)/$', DeleteDistrict, name='delete_district'),
    re_path(r'^view-district/(?P<id>[-\w]+)/$', ViewDistrict, name='view_district'),
    re_path(r'^edit-district/(?P<id>[-\w]+)/$', EditDistrict, name='edit_district'),
    
]