from .views import *
from django.contrib import admin
from django.urls import re_path
from django.urls import path

admin.autodiscover()

app_name = 'accounts'

urlpatterns = [

    ## Authentication
    re_path(r'^login/$', LoginView.as_view(), name='login'),
    re_path(r'^logout/$', LogOutView.as_view(), name='logout'),
    path("reset-password-user/<token>/",ResetPassword,name="reset_password_user"),
    re_path(r'^forgot-password-email/$', ForgotPasswordEmail, name='forgot_password_email'),
    
    ## Users
    re_path(r'^change-password/$', PasswordChange.as_view(), name='change_password'),
    re_path(r'^validations/$', Validations, name='validations'),
    re_path(r'^user-graph/$', UserGraph, name='user_graph'),

    ## Login History
    re_path(r'^login-history/$', LoginHistoryView, name='login_history'),
    re_path(r'^delete-history/$', DeleteHistory, name='delete_history'),

    ## Notifications
    # re_path(r'^notifications/$', NotificationsList, name='notifications_list'),
    # re_path(r'^delete-notifications/$', DeleteNotifications, name='delete_notifications'),
    # re_path(r'^mark-read-notifications/$', MarkReadNotifications, name='mark_read_notifications'),
    
]