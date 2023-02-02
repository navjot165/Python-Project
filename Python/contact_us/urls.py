from django.contrib import admin
from .views import *
from django.urls import re_path


admin.autodiscover()
app_name = 'contact_us'


urlpatterns = [

    ## Contact Us
    re_path(r'contact-us-list/$',ContactUsList,name="contactus_list"),
    re_path(r'view-contact-us-details/(?P<id>[-\w]+)/$',ViewContactUsDetails,name="view_contact"),
    re_path(r'delete-contact-us/(?P<id>[-\w]+)/$',DeleteContactUs,name="delete_contact"),
    re_path(r'contactus-reply/$',ContactUsReplyView,name="contactus_reply"),

]