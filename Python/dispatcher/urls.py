from django.contrib import admin
from .views import *
from django.urls import re_path


admin.autodiscover()
app_name = 'dispatcher'


urlpatterns = [

    re_path(r'^$', DispatchesList, name='dispatches_list'),
    re_path(r'^add-dispatch/$', AddDispatch, name='add_dispatch'),
    re_path(r'^view-dispatch/(?P<id>[-\w]+)/$', ViewDispatch, name='view_dispatch'),
    re_path(r'^delete-dispatch/(?P<id>[-\w]+)/$', DeleteDispatch, name='delete_dispatch'),
    re_path(r'^edit-dispatch/(?P<id>[-\w]+)/$', EditDispatch, name='edit_dispatch'),
    re_path(r'^edit-dispatch/$', ActivateDeactivateDispatch, name='activate_deactivate_dispatch'),
    re_path(r'^dispatch-manual-rides/(?P<id>[-\w]+)/$', DispatchManualRides, name='dispatch_manual_rides'),
    
]