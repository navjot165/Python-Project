from django.contrib import admin
from .views import *
from django.urls import re_path


admin.autodiscover()
app_name = 'page'


urlpatterns = [

    ## Pages
    re_path(r'pages-list/$',PagesListView,name="pages_list"),
    re_path(r'add-page/$',AddPageView,name="add_page"),
    re_path(r'^delete-page/(?P<id>[-\w]+)/$', DeletePage, name='delete_page'),
    re_path(r'^view-page/(?P<id>[-\w]+)/$', ViewPage, name='view_page'),
    re_path(r'^edit-page/(?P<id>[-\w]+)/$', EditPage, name='edit_page'),
    
]