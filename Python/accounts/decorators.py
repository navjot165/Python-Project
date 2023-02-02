from functools import wraps
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.constants import *
from accounts.models import *
from django.contrib.auth.models import Permission


def admins_only(function):
    @login_required
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_superuser:
            return function(request, *args, **kwargs)
        else:
            return render(request, 'frontend/404.html')
    return wrap


def check_permissions(permission):
    def wrap(view_method):
        def arguments_wrapper(request, *args, **kwargs):
            if request.user.role_id == SUBADMIN:
                try:
                    permission_object = Permission.objects.get(codename=permission.split('.')[1],content_type__app_label=permission.split('.')[0])
                except:
                    permission_object = None
                if permission_object:
                    if not User.user_permissions.through.objects.filter(permission=permission_object,user=request.user):
                        return render(request, 'frontend/restrict.html')
                    else:
                        return view_method(request, *args, **kwargs)
                else:
                    return view_method(request, *args, **kwargs)
            else:
                return view_method(request, *args, **kwargs)
        return arguments_wrapper
    return wrap