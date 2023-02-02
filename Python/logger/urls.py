from django.contrib import admin
from .views import *
from django.urls import re_path


admin.autodiscover()
app_name = 'logger'


urlpatterns = [

    ## Error Logs
    re_path(r'error-logs/$',ErrorLogsList,name="error_logs_list"),
    re_path(r'delete-all-logs/$',DeleteAllLogs,name="delete_all_logs"),
    re_path(r'delete-error-log/(?P<id>[-\w]+)/$',DeleteErrorLog,name="delete_error_log"),
    re_path(r'view-error-log/(?P<id>[-\w]+)/$',ViewErrorLog,name="view_error_log"),

    ## Email Logger
    re_path(r'email-logs/$',EmailLogsList,name="email_logs_list"),
    re_path(r'email-logs-delete/$',DeleteEmailLogs,name="delete_email_logs"),
    re_path(r'view-email-log/(?P<id>[-\w]+)/$',ViewEmailLog,name="view_email_log"),
    re_path(r'delete-email-log/(?P<id>[-\w]+)/$',DeleteEmailLog,name="delete_email_log"),

    ## Action Logger
    re_path(r'action-logs/$',ActionLogsList,name="action_logs_list"),
    re_path(r'delete-all-action-log/$',DeleteActionLogs,name="delete_action_logs"),
    re_path(r'view-action-log/(?P<id>[-\w]+)/$',ActionEmailLog,name="view_action_log"),
    re_path(r'delete-action-log/(?P<id>[-\w]+)/$',DeleteActionLog,name="delete_action_log"),

    ## Application Crash Logs
    re_path(r'create-crash-log/$',CreateCrashLog.as_view(),name="create_crash_log"),
    re_path(r'crash-logs/$',CrashLogs,name="crash_logs"),
    re_path(r'crash-logs-delete/$',DeleteAllCrashLogs,name="delete_all_crash_logs"),
    re_path(r'delete-crash-log/(?P<id>[-\w]+)/$',DeleteCrashLog,name="delete_crash_log"),
    re_path(r'view-crash-log/(?P<id>[-\w]+)/$',ViewCrashLog,name="view_crash_log"),
    
]