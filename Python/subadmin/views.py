import logging
from accounts.decorators import *
from accounts.helper import *
from accounts.utils import *
from holidays.models import *
from cities.models import *
from routes.models import *
from frontend.views import *
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from .models import *
from .helper import *
db_logger = logging.getLogger('db')


@admins_only
def SubadminsList(request):
    users = User.objects.filter(role_id=SUBADMIN).order_by('-created_on')
    return render(request, 'subadmin/subadmins-list.html',{
        "head_title":"Sub-Admins Management",
        "users":get_pagination(request, users)
    })


@admins_only
def AddSubadmin(request):
    if request.method == 'POST':
        user = User.objects.create(
            first_name = request.POST.get("first_name"),
            last_name = request.POST.get("last_name"),
            full_name = request.POST.get("first_name") + " " + request.POST.get("last_name") if request.POST.get("last_name") else request.POST.get("first_name"),
            email = request.POST.get("email"),
            mobile_no = request.POST.get("mobile_no"),
            country_code = request.POST.get("country_code"),
            password = make_password(request.POST.get("password")),
            role_id = SUBADMIN,
            gender = request.POST.get("gender"),
            is_profile_verified = True,
            profile_pic = request.FILES.get('profile_pic') if request.FILES.get('profile_pic') else None,
            city = Cities.objects.get(id=request.POST.get('city')),
            is_superuser = True,
            is_staff = True
        )
        try:
            wallet = UserWallet.objects.get(user=user)
        except:
            wallet = UserWallet.objects.create(user=user)
        SendUserEmail(request,user,'EmailTemplates/CaptainPassword.html','Registration confirmation',request.POST.get("email"),"","","",request.POST.get("password"))
        messages.success(request, 'Sub-Admin Created Successfully!')
        return redirect('users:view_user', id=user.id)
    return render(request, 'subadmin/add-subadmin.html',{
        "head_title":"Sub-Admins Management",
        "cities":Cities.objects.all()
    })


@admins_only
def EditSubadmin(request,id):
    user = User.objects.get(id=id)
    if request.method == 'POST':
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.full_name = request.POST.get("first_name") + " " + request.POST.get("last_name") if request.POST.get("last_name") else request.POST.get("first_name")
        user.email = request.POST.get("email")
        user.mobile_no = request.POST.get("mobile_no")
        user.country_code = request.POST.get("country_code")
        user.gender = request.POST.get("gender")
        user.city = Cities.objects.get(id=request.POST.get('city'))
        if request.FILES.get("profile_pic"):
            user.profile_pic = request.FILES.get('profile_pic')
        user.save()
        messages.success(request, 'Sub-Admin Updated Successfully!')
        return redirect('users:view_user', id=user.id)
    return render(request, 'subadmin/edit-subadmin.html',{
        "head_title":"Sub-Admins Management",
        "cities":Cities.objects.all(),
        "user":user
    })


@admins_only
def AssignPermissionSubadmin(request,id):
    user = User.objects.get(id=id)
    user_permissions = [permission.permission_id for permission in User.user_permissions.through.objects.filter(user_id=id)]
    if request.method == 'POST':
        User.user_permissions.through.objects.filter(user_id=id).delete()
        if request.POST.getlist('permissions'):
            [user.user_permissions.add(Permission.objects.get(id=permission_id))for permission_id in request.POST.getlist('permissions')]
        messages.success(request, 'Permissions Assigned Successfully!')
        return redirect('users:view_user', id=user.id)
    return render(request, 'subadmin/assign-permissions.html',{
        "head_title":"Sub-Admins Management",
        "user":user,
        "permissions":GetPermissionsList(),
        "user_permissions":user_permissions
    })
