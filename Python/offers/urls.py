from django.contrib import admin
from .views import *
from django.urls import re_path


admin.autodiscover()
app_name = 'offers'


urlpatterns = [

    re_path(r'offers-list/$',OffersList,name="offers_list"),
    re_path(r'add-offer/$',AddOffer,name="add_offer"),
    re_path(r'activate-deactivate-offer/$',ActivateDeactivateOffer,name="activate_deactivate_offer"),
    re_path(r'view-offer/(?P<id>[-\w]+)/$',ViewOffer,name="view_offer"),
    re_path(r'delete-offer/(?P<id>[-\w]+)/$',DeleteOffer,name="delete_offer"),
    re_path(r'edit-offer/(?P<id>[-\w]+)/$',EditOffer,name="edit_offer"),

]