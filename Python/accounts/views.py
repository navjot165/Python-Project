import re
import logging
from accounts.decorators import *
from accounts.utils import *
from .models import *
from frontend.views import *
from datetime import datetime
from django.db.models import Q
from django.db.models import Count
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import View
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from rest_framework.authtoken.models import Token
from user_agents import parse
db_logger = logging.getLogger('db')




class AdminLoginView(TemplateView):
    def get(self, request, *args, **kwargs):
        return redirect('accounts:login')

      
class LogOutView(View):
    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect('accounts:login')


class LoginView(View):
    def get(self,request,*args,**kwargs):
        return render(request,'registration/login.html')

    def post(self,request,*args,**kwargs):
        email = request.POST.get("email")
        password = request.POST.get("password")
        des= request.path
        urls="http://"+request.META.get("REMOTE_ADDR")+des
        if not email:
            return render(request, 'registration/login.html',{"email":email,"password":password})
        if not password:
            return render(request, 'registration/login.html',{"email":email,"password":password})
        if request.POST.get('remember_me')=='on':    
           request.session.set_expiry(1209600) 
        try:
            user = authenticate(username=email, password=password)
        except Exception as e:
            user = None
        if not user:
            LoginHistory.objects.create(User_Ip=request.META.get("REMOTE_ADDR"),User_agent=str(parse(request.META['HTTP_USER_AGENT'])),State="Failed",Code=urls,user=user)
            messages.error(request, 'Invalid login details.')
            return render(request, 'registration/login.html',{"email":email,"password":password})
        if user.is_superuser and user.role_id == ADMIN:
            login(request, user)
            LoginHistory.objects.create(User_Ip=request.META.get("REMOTE_ADDR"),User_agent=str(parse(request.META['HTTP_USER_AGENT'])),State="Success",Code=urls,user=user)
            if request.POST.get('latitude') and request.POST.get('longitude'):
                user.latitude = request.POST.get('latitude')
                user.longitude = request.POST.get('longitude')
                user.location = request.POST.get('location') if request.POST.get('location') else None
                user.short_location = request.POST.get('short_location') if request.POST.get('short_location') else None
                user.save()
            return redirect('admin:index')
        elif user.role_id == SUBADMIN:
            if user.status == DELETED:
                LoginHistory.objects.create(User_Ip=request.META.get("REMOTE_ADDR"),User_agent=str(parse(request.META['HTTP_USER_AGENT'])),State="Failed",Code=urls,user=user)
                messages.error(request, 'Your account has been deleted.')
                return render(request, 'registration/login.html',{"email":email,"password":password})
            elif user.status == INACTIVE:
                LoginHistory.objects.create(User_Ip=request.META.get("REMOTE_ADDR"),User_agent=str(parse(request.META['HTTP_USER_AGENT'])),State="Failed",Code=urls,user=user)
                messages.error(request, 'Your account has been deactivated.')
                return render(request, 'registration/login.html',{"email":email,"password":password})
            else:
                login(request, user)
                LoginHistory.objects.create(User_Ip=request.META.get("REMOTE_ADDR"),User_agent=str(parse(request.META['HTTP_USER_AGENT'])),State="Success",Code=urls,user=user)
                if request.POST.get('latitude') and request.POST.get('longitude'):
                    user.latitude = request.POST.get('latitude')
                    user.longitude = request.POST.get('longitude')
                    user.location = request.POST.get('location') if request.POST.get('location') else None
                    user.short_location = request.POST.get('short_location') if request.POST.get('short_location') else None
                    user.save()
                return redirect('admin:index')
        messages.error(request, 'Invalid login details.')
        return render(request, 'registration/login.html',{"email":email,"password":password})


class PasswordChange(View):
    @method_decorator(login_required)
    def get(self,request,*args,**kwargs):
        return render(request,'admin/change-password.html',{"head_title":"Change Password"})

    def post(self,request,*args,**kwargs):
        if request.POST.get('user_id'):
            user = User.objects.get(id=request.POST.get('user_id'))
        else:
            user = User.objects.get(id=request.user.id)
        user.set_password(request.POST.get("password"))
        user.save()
        messages.add_message(request, messages.INFO, 'Password changed successfully')
        if request.POST.get('user_id'):
            SendUserEmail(request,user,'EmailTemplates/AccountStatus.html','Account Password Changed',user.email,"","Your account password has been changed by the admin. Please use the below mentioned password to login to your account.",'Account Password Changed',request.POST.get("password"))
            return redirect('users:view_user',id=user.id)
        else:
            return redirect('accounts:login')


@admins_only
def LoginHistoryView(request):
    loginhistory = LoginHistory.objects.all().order_by('-create_time')
    loginhistory = get_pagination(request,loginhistory)
    return render(request, 'admin/login-history.html', {"loginhistory":loginhistory,"head_title":"Login History"})


@admins_only
def DeleteHistory(request):
    history=LoginHistory.objects.all()
    if history:
        history.delete()
        messages.success(request,"All Login History Cleared Sucessfully!!!")
    else:
        messages.error(request,"Nothing to Delete!!!")
    return redirect('accounts:login_history')

 
def Validations(request):
    if request.is_ajax():
        data ={"valid":None, "email_exists":None, "mobile_exists":None}
        if request.GET.get("email"):
            match = str(re.search(r'^[a-zA-Z0-9_.+-]+[@]\w+[.]\w{2,3}$',request.GET.get("email").strip()))    
            if match != "None":
                data['valid'] = '1'
            else:
                data['valid'] = '0'

        if request.GET.get("email") and request.GET.get('role_id'):
            email_users = User.objects.filter(Q(status = ACTIVE) | Q(status = INACTIVE),role_id=int(request.GET.get('role_id')), email = request.GET.get("email"))
            if request.GET.get('user'):
                email_users = email_users.exclude(id=request.GET.get('user'))
            if email_users:
                data['email_exists'] = '1'
            else:
                data['email_exists'] = '0'
        else:
            data['email_exists'] = '0'

        if request.GET.get("mobile_no") and request.GET.get('country_code'):
            mobile_users = User.objects.filter(Q(status = ACTIVE) | Q(status = INACTIVE),role_id=int(request.GET.get('role_id')), mobile_no = request.GET.get("mobile_no"),country_code=request.GET.get('country_code'))
            if request.GET.get('user'):
                mobile_users = mobile_users.exclude(id=request.GET.get('user'))
            if mobile_users:
                data['mobile_exists'] = '1'
            else:
                data['mobile_exists'] = '0'
        else:
            data['mobile_exists'] = '0'
        return JsonResponse(data)


def ResetPassword(request,token):
    if request.method =='GET':
        token = Token.objects.get(key=token)
        user = User.objects.get(id=token.user_id)
        return render(request,'registration/ResetPassword.html',{"token":token})
    if request.method == 'POST':
        token = Token.objects.get(key=token)
        user = User.objects.get(id=token.user_id)
        new_password = request.POST.get("password")
        user = User.objects.get(id=token.user_id)
        user.set_password(new_password)
        user.save()
        token.delete()
        messages.success(request,'Password reset successfully!')
        return redirect('accounts:login')


def ForgotPasswordEmail(request):
    if request.method=='POST':
        if not User.objects.filter(Q(status=ACTIVE)|Q(status=INACTIVE),email=request.POST.get("email")).exists():
            messages.success(request,'Please enter a valid email id.')
            return redirect('accounts:forgot_password_email')
        else:
            user = User.objects.filter(Q(status=ACTIVE)|Q(status=INACTIVE),email=request.POST.get("email")).last()
            try:
                token = Token.objects.get(user=user)
            except:
                token = Token.objects.create(user=user)  
            SendUserEmail(request,user,'EmailTemplates/ResetPassword.html','Reset Password',request.POST.get("email"),token,"","","")
            messages.success(request,'A link has been sent on your email to reset your password.')
            return redirect('accounts:login')
    return render(request, 'registration/forgot-email.html')


@admins_only
def UserGraph(request):
    customers, captains, subadmins = [],[],[]
    months = {'jan':'1','feb':'2','mar':'3','apr':'4','may':'5','jun':'6','jul':'7','aug':'8','sep':'9','oct':'10','nov':'11','dec':'12'}
    for i in months.keys():
        customers.append(User.objects.filter(created_on__year=str(datetime.now().year),created_on__month= months[i],role_id=CUSTOMER).exclude(role_id=ADMIN).annotate(count=Count('id')).count())
        captains.append(User.objects.filter(created_on__year=str(datetime.now().year),created_on__month= months[i],role_id=CAPTAIN).exclude(role_id=ADMIN).annotate(count=Count('id')).count())
        subadmins.append(User.objects.filter(created_on__year=str(datetime.now().year),created_on__month= months[i],role_id=SUBADMIN).exclude(role_id=ADMIN).annotate(count=Count('id')).count())
    chart = {
        'chart': {'type': 'column'}, 
        'title': {'text': f'Users in {datetime.now().year}'},
        'xAxis': { 'categories': [i.upper() for i in months.keys()]},
        'colors': ['#fe7096','#047edf','#e181ec',],
        'series': [
            {
                'name': 'Customers',
                'data':customers
            },
            {
                'name': 'Captains',
                'data':captains
            },
            {
                'name': 'Sub-Admins',
                'data':subadmins
            },
        ],
        'accessibility': {
            'enabled': False
        },
        'plotOptions': {'column': { 'borderRadius': '5' }}
    }
    return JsonResponse(chart)


# @admins_only
# def NotificationsList(request):
#     notifications = Notification.objects.filter(created_for=request.user).order_by('-created_on')
#     return render(request, "admin/notifications.html",{
#         "head_title": "Notifications Management",
#         "notifications": get_pagination(request, notifications)
#     })


# @admins_only
# def DeleteNotifications(request):
#     notifications = Notification.objects.filter(created_for=request.user)
#     if notifications:
#         notifications.delete()
#         messages.success(request, 'Notifications Deleted Successfully!')
#     else:
#         messages.error(request, "No Notifications to Delete!")
#     return redirect('accounts:notifications_list')


# @admins_only
# def MarkReadNotifications(request):
#     notifications = Notification.objects.filter(created_for=request.user)
#     if notifications:
#         notifications.update(is_read=True)
#         messages.success(request, 'All Notifications Marked As Read Successfully!')
#     else:
#         messages.error(request, "No Notifications to Read!")
#     return redirect('accounts:notifications_list')