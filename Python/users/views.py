import logging
from accounts.decorators import *
from accounts.utils import *
from .models import *
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import render, redirect
from rest_framework.authtoken.models import Token
from captains.models import *
from subadmin.helper import *
db_logger = logging.getLogger('db')
from django.contrib.auth.models import Permission


@admins_only
def EditUser(request,id):
    user = User.objects.get(id=id)
    if request.method == "POST":
        email_users = User.objects.filter(Q(status = ACTIVE) | Q(status = INACTIVE),Q(role_id=CAPTAIN)|Q(role_id=CUSTOMER), email = request.POST.get("email")).exclude(id=id)
        username_users = User.objects.filter(Q(status = ACTIVE) | Q(status = INACTIVE),Q(role_id=CAPTAIN)|Q(role_id=CUSTOMER), username = request.POST.get("username")).exclude(id=id)
        if username_users:
            messages.success(request,"Username already exists")
            return render(request, 'admin/edit-admin.html',{"head_title":"Admin Profile","user":user}) 
        if email_users:
            messages.success(request,"Email already exists")
            return render(request, 'admin/edit-admin.html',{"head_title":"Admin Profile","user":user}) 
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        if request.FILES.get('profile_pic'):
            user.profile_pic = request.FILES.get('profile_pic')
        user.save()
        messages.success(request,"Profile updated successfully!")
        return redirect('users:view_user',id=user.id)
    return render(request, 'admin/edit-admin.html',{"head_title":"Admin Profile","user":user})


@admins_only
def ViewUser(request,id):
    user = User.objects.get(id=id)
    if request.GET.get('n_id'):
        Notification.objects.filter(id=request.GET.get('n_id')).update(is_read=True)
    if user.role_id == ADMIN:
        return render(request, 'admin/admin-profile.html', {"user":user,"head_title":"Admin Profile"})
    elif user.role_id == CUSTOMER:
        if request.user.role_id == SUBADMIN:
            permission_object = Permission.objects.get(codename='view_customer')
            if not User.user_permissions.through.objects.filter(permission=permission_object,user=request.user):
                return render(request, 'frontend/restrict.html')
        return render(request, 'users/customer-profile.html', {"user":user,"head_title":"Profile Management","showCustomer":True})
    elif user.role_id == CAPTAIN:
        if request.user.role_id == SUBADMIN:
            permission_object = Permission.objects.get(codename='view_captain')
            if not User.user_permissions.through.objects.filter(permission=permission_object,user=request.user):
                return render(request, 'frontend/restrict.html')
        captain = Captain.objects.get(user=user)
        assigned_bus = AssignedCaptainBuses.objects.filter(captain = captain)
        return render(request, 'captains/captain-profile.html', {"user":user,"captain":captain,"head_title":"Profile Management","showCaptain":True,"assigned_bus":assigned_bus})
    elif user.role_id == SUBADMIN:
        user_permissions = [permission.permission_id for permission in User.user_permissions.through.objects.filter(user_id=id)]
        return render(request, 'subadmin/subadmin-profile.html', {"user":user,"head_title":"Profile Management","permissions":GetPermissionsList(),
        "user_permissions":user_permissions,"showSubAdmin":True})


@admins_only
def InactivateUser(request,id):
    user = User.objects.get(id=id)
    if request.user.role_id == SUBADMIN:
        if user.role_id == CUSTOMER:
            permission_object = Permission.objects.get(codename='activate_deactivate_delete_customer')
        elif user.role_id == CAPTAIN:
            permission_object = Permission.objects.get(codename='activate_deactivate_delete_captain')
        if permission_object:
            if not User.user_permissions.through.objects.filter(permission=permission_object,user=request.user):
                return render(request, 'frontend/restrict.html')
    user.status = INACTIVE
    user.save()
    Token.objects.filter(user=user).delete()
    messages.success(request,'User Account Deactivated Successfully!')
    SendUserEmail(request,user,'EmailTemplates/AccountStatus.html','Account Deactivated',user.email,"","Your account has been deactivated. Please contact admin to activate your account.",'Account Deactivated',"")
    return redirect('users:view_user',id=user.id)


@admins_only
def DeleteUser(request,id):
    user = User.objects.get(id=id)
    if request.user.role_id == SUBADMIN:
        if user.role_id == CUSTOMER:
            permission_object = Permission.objects.get(codename='activate_deactivate_delete_customer')
        elif user.role_id == CAPTAIN:
            permission_object = Permission.objects.get(codename='activate_deactivate_delete_captain')
        if permission_object:
            if not User.user_permissions.through.objects.filter(permission=permission_object,user=request.user):
                return render(request, 'frontend/restrict.html')
    user.status = DELETED
    user.save()
    Token.objects.filter(user=user).delete()
    messages.success(request,'User Account Deleted Successfully!')
    SendUserEmail(request,user,'EmailTemplates/AccountStatus.html','Account Deleted',user.email,"","Your account has been deleted. Please contact admin to activate your account.",'Account Deleted',"")
    return redirect('users:view_user',id=user.id)


@admins_only
def ActivateUser(request,id):
    user = User.objects.get(id=id)
    if request.user.role_id == SUBADMIN:
        if user.role_id == CUSTOMER:
            permission_object = Permission.objects.get(codename='activate_deactivate_delete_customer')
        elif user.role_id == CAPTAIN:
            permission_object = Permission.objects.get(codename='activate_deactivate_delete_captain')
        if permission_object:
            if not User.user_permissions.through.objects.filter(permission=permission_object,user=request.user):
                return render(request, 'frontend/restrict.html')
    user.status = ACTIVE
    user.save()
    messages.success(request,'User Account Activated Successfully!')
    SendUserEmail(request,user,'EmailTemplates/AccountStatus.html','Account Activated',user.email,"","Your account has been activated.",'Account Activated',"")
    return redirect('users:view_user',id=user.id)


@admins_only
@check_permissions('users.customers_list')
def AllCustomers(request):
    users = User.objects.filter(role_id=CUSTOMER).order_by('-created_on')
    if request.GET.get('full_name'):
        users = users.filter(full_name__icontains = request.GET.get('full_name'))
    if request.GET.get('email'):
        users = users.filter(email__icontains = request.GET.get('email'))
    if request.GET.get('mobile_no'):
        users = users.filter(mobile_no__icontains = request.GET.get('mobile_no'))
    if request.GET.get('created_on'):
        users = users.filter(created_on__date = request.GET.get('created_on'))
    if request.GET.get('status'):
        users = users.filter(status=request.GET.get('status'))
    if request.GET and not users:
        messages.error(request, 'No Data Found')
    return render(request, 'users/all-customers.html', {
        "users": get_pagination(request, users),
        "head_title":"Customers Management",
        "full_name":request.GET.get('full_name') if request.GET.get('full_name') else "",
        "email":request.GET.get('email') if request.GET.get('email') else "",
        "mobile_no":request.GET.get('mobile_no') if request.GET.get('mobile_no') else "",
        "created_on":request.GET.get('created_on') if request.GET.get('created_on') else "",
        "status":request.GET.get('status') if request.GET.get('status') else "",
    })


@admins_only
@check_permissions('captains.captains_list')
def AllCaptains(request):
    users = User.objects.filter(role_id=CAPTAIN).order_by('-created_on')
    if request.GET.get('full_name'):
        users = users.filter(full_name__icontains = request.GET.get('full_name'))
    if request.GET.get('email'):
        users = users.filter(email__icontains = request.GET.get('email'))
    if request.GET.get('mobile_no'):
        users = users.filter(mobile_no__icontains = request.GET.get('mobile_no'))
    if request.GET.get('created_on'):
        users = users.filter(created_on__date = request.GET.get('created_on'))
    if request.GET.get('is_profile_verified'):
        users = users.filter(is_profile_verified = request.GET.get('is_profile_verified'))
    if request.GET.get('status'):
        users = users.filter(status=request.GET.get('status'))
    if request.GET and not users:
        messages.error(request, 'No Data Found')
    return render(request, 'captains/all-captains.html', {
        "users": get_pagination(request, users),
        "head_title":"Captains Management",
        "full_name":request.GET.get('full_name') if request.GET.get('full_name') else "",
        "email":request.GET.get('email') if request.GET.get('email') else "",
        "mobile_no":request.GET.get('mobile_no') if request.GET.get('mobile_no') else "",
        "created_on":request.GET.get('created_on') if request.GET.get('created_on') else "",
        "status":request.GET.get('status') if request.GET.get('status') else "",
        "is_profile_verified":request.GET.get('is_profile_verified') if request.GET.get('is_profile_verified') else "",
    })
    

@admins_only 
@check_permissions('accounts.edit_customer')
def EditCustomer(request,id):
    user = User.objects.get(id=id)
    if request.method == 'POST':
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.full_name = request.POST.get("first_name") + " " + request.POST.get("last_name") if request.POST.get("last_name") else request.POST.get("first_name")
        user.email = request.POST.get("email")
        user.mobile_no = request.POST.get("mobile_no")
        user.country_code = request.POST.get("country_code")
        user.gender = request.POST.get("gender")
        if request.FILES.get('profile_pic'):
            user.profile_pic = request.FILES.get('profile_pic')
        user.save()
        messages.success(request, 'Customer Profile Updated Successfully!')
        return redirect('users:view_user', id=user.id)
    return render(request, 'users/edit-customer.html',{"head_title":"Customers Management",'user':user})
