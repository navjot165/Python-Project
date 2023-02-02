from .views import *
from django.contrib import admin
from django.urls import re_path

admin.autodiscover()

app_name = 'users'

urlpatterns = [
    ## Users
    re_path(r'^view-profile/(?P<id>[-\w]+)/$',ViewUser, name='view_user'),
    re_path(r'^edit-profile/(?P<id>[-\w]+)/$',EditUser, name='edit_user'),

    re_path(r'^customers-list/$',AllCustomers, name='all_customers'),
    re_path(r'^captains-list/$',AllCaptains, name='all_captains'),

    ## User Actions
    re_path(r'^deactivate-user/(?P<id>[-\w]+)/$',InactivateUser, name='inactivate_user'),
    re_path(r'^delete-user/(?P<id>[-\w]+)/$',DeleteUser, name='delete_user'),
    re_path(r'^activate-user/(?P<id>[-\w]+)/$',ActivateUser, name='activate_user'),

    ## Customers
    re_path(r'^edit-customer/(?P<id>[-\w]+)/$',EditCustomer, name='edit_customer'),

]