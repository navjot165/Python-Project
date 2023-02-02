from django.contrib import admin
from .views_authentication import *
from .views_customer import *
from .views_captain import *
from django.urls import re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


admin.autodiscover()
app_name = 'api'


# schema_view = get_schema_view(
#     openapi.Info(
#         title = "Basigo API's",
#         description = "API documentation for Basigo Project",
#         default_version = "v1",
#         terms_of_service = "https://www.google.com/policies/terms/",
#         contact = openapi.Contact(email="contact@snippets.local"),
#         license = openapi.License(name="BSD License"),
#     ),
#     public=True,
#     permission_classes=(permissions.AllowAny,),
# )


urlpatterns = [

    ## Documentation
    # re_path("/",schema_view.with_ui("swagger", cache_timeout=0),name="schema-swagger-ui"),
    # re_path("api-docs/",schema_view.with_ui("redoc", cache_timeout=0),name="schema-redoc"),

    ## Authentication
    re_path(r'user-login/$', LoginView.as_view(), name='login'),
    re_path(r'signup/$', SignupCustomerView.as_view(), name='signup_customer'),
    re_path(r'cities-list/$', CitiesList.as_view(), name='cities_list'),
    re_path(r'signup-captain/$', SignupCaptainView.as_view(), name='signup_captain'),
    re_path(r'verify-otp/$', VerifyOTP.as_view(), name='verify_otp'),
    re_path(r'resend-otp/$', ResendOTP.as_view(), name='resend_otp'),
    re_path(r'logout/$', LogoutView.as_view(), name='logout'),
    re_path(r'check-user/$', UserCheckView.as_view(), name='check_user'),
    re_path(r'edit-profile/$', EditProfileCustomer.as_view(), name='edit_profile_customer'),
    re_path(r'update-city/$', UpdateUserCity.as_view(), name='update_user_city'),
    re_path(r'edit-profile-captain/$', EditProfileCaptain.as_view(), name='edit_profile_captain'),
    re_path(r'get-profile-details/$', GetProfileDetails.as_view(), name='get_profile_details'),
    re_path(r'forget-password/$',ForgetPassword.as_view(),name="forget_password"),
    re_path(r'change-password/$',ChangePassword.as_view(),name="change_password"),
    re_path(r'static-pages/$',StaticPages.as_view(),name="static_pages"),
    re_path(r'delete-account/$',DeleteAccount.as_view(),name="delete_account"),
    re_path(r'delete-document/$',DeleteDocuments.as_view(),name="delete_documents"),
    re_path(r'contactus-view/$',ContactUsView.as_view(),name="contact_us_view"),

    ## Customers
    re_path(r'available-routes-list/$',AvailableRoutesList.as_view(),name="available_routes_list"),
    re_path(r'pickup-dropoff-stations/$',PickupDropoffStations.as_view(),name="pickup_dropoff_stations"),
    re_path(r'rides-dates-list/$',RidesDatesList.as_view(),name="rides_dates_list"),
    re_path(r'rides-date-selection/$',RidesDateSelection.as_view(),name="rides_date_selection"),
    re_path(r'create-booking/$',CreateBooking.as_view(),name="create_booking"),
    re_path(r'customer-bookings-list/$',BookingsList.as_view(),name="bookings_list"),
    re_path(r'booking-details/$',BookingDetails.as_view(),name="booking_details"),
    re_path(r'cancel-booking/$',CancelBooking.as_view(),name="cancel_booking"),
    re_path(r'customer-transactions/$',CustomerTransactions.as_view(),name="customer_transactions"),
    re_path(r'review-texts-list/$',ReviewTextsView.as_view(),name="review_texts_list"),
    re_path(r'rate-ride/$',RateRide.as_view(),name="rate_ride"),
    re_path(r'cancellation-reasons-list/$',CancellationReasonsList.as_view(),name="cancellation_reasons"),    
    re_path(r'search-ride-datetime/$',SearchRideDatetime.as_view(),name="search_ride_datetime"),  
    re_path(r'customer-offers-list/$',CustomerOffersList.as_view(),name="customer_offers_list"),  
    re_path(r'get-ride-location/$',GetRideLocation.as_view(),name="get_ride_location"),

    ## Captains
    re_path(r'assigned-rides/$',AssignedRides.as_view(),name="assigned_rides"),
    re_path(r'assigned-ride-details/$',AssignedRideDetails.as_view(),name="assigned_ride_details"),
    re_path(r'admin-start-ride/$',StartRide.as_view(),name="start_ride"),
    re_path(r'admin-end-ride/$',EndRide.as_view(),name="end_ride"),
    re_path(r'station-passengers-list/$',StationPassengersList.as_view(),name="station_passengers_list"),
    re_path(r'change-booking-state/$',ChangeBookingState.as_view(),name="change_booking_state"),
    re_path(r'update-ride-location/$',UpdateRideLocation.as_view(),name="update_ride_location"),

]