import logging
from .models import *
from django.shortcuts import render, redirect
from django.contrib import messages
from django_db_logger .models import StatusLog
from accounts.decorators import *
from accounts.utils import get_pagination
from api.models import *
from rest_framework.views import APIView
from rest_framework import status,permissions
from rest_framework.response import Response
db_logger = logging.getLogger('db')


@admins_only
def ErrorLogsList(request):
    error_logs = StatusLog.objects.all().order_by('-create_datetime')
    error_logs = get_pagination(request,error_logs)
    return render(request, 'logger/error-logs-list.html',{"head_title":"Website Error Logs Management","error_logs":error_logs})


@admins_only
def DeleteAllLogs(request):
    StatusLog.objects.all().delete()
    messages.success(request,"Error Logs Deleted Successfully!")
    return redirect('logger:error_logs_list')


@admins_only
def DeleteErrorLog(request,id):
    StatusLog.objects.get(id=id).delete()
    messages.success(request,"Error Log Deleted Successfully!")
    return redirect('logger:error_logs_list')


@admins_only
def ViewErrorLog(request,id):
    error_log = StatusLog.objects.get(id=id)
    return render(request, 'logger/view-error-log.html',{"head_title":"Website Error Logs Management","error_log":error_log})


@admins_only
@check_permissions('logger.email_logs_list')
def EmailLogsList(request):
    email_logs = EmailLogger.objects.all().order_by('-created_on')
    email_logs = get_pagination(request,email_logs)
    return render(request, 'email-logger/email-logs-list.html',{"head_title":"Email Logs Management","email_logs":email_logs})


@admins_only
@check_permissions('logger.clear_email_logs')
def DeleteEmailLogs(request):
    if EmailLogger.objects.all():
        EmailLogger.objects.all().delete()
        messages.success(request,"Email Logs Deleted Successfully!")
    else:
        messages.error(request,"No Email Logs Found!")
    return redirect('logger:email_logs_list')


@admins_only
@check_permissions('logger.view_email_log')
def ViewEmailLog(request, id):
    email_log = EmailLogger.objects.get(id=id)
    return render(request, 'email-logger/view-email-log.html',{"head_title":"Email Logs Management","email_log":email_log})


@admins_only
@check_permissions('logger.delete_email_log')
def DeleteEmailLog(request, id):
    EmailLogger.objects.get(id=id).delete()
    messages.success(request, 'Email Log Deleted Successfully!')
    return redirect('logger:email_logs_list')


@admins_only
def ActionLogsList(request):
    action_logs = ActionActivityLogs.objects.all().order_by('created_on')
    action_logs = get_pagination(request,action_logs)
    return render(request, 'action-logger/action-logs-list.html',{"head_title":"Action Logs Management","action_logs":action_logs})


@admins_only
def DeleteActionLogs(request):
    if ActionActivityLogs.objects.all():
        ActionActivityLogs.objects.all().delete()
        messages.success(request,"Action Activity Logs Deleted Successfully!")
    else:
        messages.error(request,"No Action Logs Found!")
    return redirect('logger:action_logs_list')


@admins_only
def ActionEmailLog(request, id):
    action_log = ActionActivityLogs.objects.get(id=id)
    return render(request, 'action-logger/view-action-log.html',{"head_title":"Action Logs Management","action_log":action_log})


@admins_only
def DeleteActionLog(request, id):
    ActionActivityLogs.objects.get(id=id).delete()
    messages.success(request, 'Action Log Deleted Successfully!')
    return redirect('logger:action_logs_list')


class CreateCrashLog(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            ApplicationCrashLogs.objects.create(
                error = request.data.get('error'),
                link = request.data.get('link'),
                referer_link = request.data.get('referer_link'),
                user_ip = request.data.get('user_ip'),
                description = request.data.get('description')
            )
        except Exception as e:
            db_logger.exception(e)
        return Response({"message":"Crash Log Created Successfully!","status":status.HTTP_200_OK}, status=status.HTTP_200_OK)


@admins_only
@check_permissions('logger.application_crashes_list')
def CrashLogs(request):
    logs = ApplicationCrashLogs.objects.all().order_by('-created_on')
    logs = get_pagination(request,logs)
    return render(request, 'application-logger/application-logs-list.html',{"head_title":"Application Error Logs Management","logs":logs})


@admins_only
@check_permissions('logger.clear_application_crashes')
def DeleteAllCrashLogs(request):
    if ApplicationCrashLogs.objects.all():
        ApplicationCrashLogs.objects.all().delete()
        messages.success(request,"Application Error Logs Deleted Successfully!")
    else:
        messages.error(request,"No Error Logs Found!")
    return redirect('logger:crash_logs')


@admins_only
@check_permissions('logger.delete_application_crash')
def DeleteCrashLog(request, id):
    ApplicationCrashLogs.objects.get(id=id).delete()
    messages.success(request, 'Error Log Deleted Successfully!')
    return redirect('logger:crash_logs')


@admins_only
@check_permissions('logger.view_application_crash')
def ViewCrashLog(request, id):
    log = ApplicationCrashLogs.objects.get(id=id)
    return render(request, 'application-logger/view-application-log.html',{"head_title":"Application Error Logs Management","log":log})