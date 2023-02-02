from django.contrib import admin
from .views import *
from django.urls import re_path


admin.autodiscover()
app_name = 'subadmin'


urlpatterns = [

    re_path(r'subadmins-list/$',SubadminsList,name="subadmin_list"),
    re_path(r'add-subadmin/$',AddSubadmin,name="add_subadmin"),
    re_path(r'edit-subadmin/(?P<id>[-\w]+)/$',EditSubadmin,name="edit_subadmin"),
    re_path(r'assign-permissions-subadmin/(?P<id>[-\w]+)/$',AssignPermissionSubadmin,name="assign_permisions_subadmin"),

]