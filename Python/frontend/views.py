from django.shortcuts import render,redirect
from accounts.constants import *
import logging
from page.models import *
db_logger = logging.getLogger('db')
 

def index(request):
    if request.user.is_authenticated and request.user.is_superuser and (request.user.role_id == ADMIN or request.user.role_id == SUBADMIN):
        return redirect('admin:index')
    else:
        return render(request, "frontend/index.html", {"showclass":True})


def handler404(request, exception, template_name="frontend/404.html"):
    db_logger.exception(exception)
    return render(request, template_name, status=404)
    

def handler500(request, *args, **kwargs):
    db_logger.exception(Exception)
    return render(request, 'frontend/404.html', status=500)
    

def handler403(request, exception, template_name="frontend/404.html"):
    db_logger.exception(exception)
    return render(request, template_name, status=403)
    

def handler400(request, exception, template_name="frontend/404.html"):
    db_logger.exception(exception)
    return render(request, template_name, status=400)


def AboutUsview(request):
    try:
        about_us = Pages.objects.get(type_id=ABOUT_US)
    except:
        about_us = None
    return render(request, "frontend/aboutus.html",{"about_us":about_us,"about_us_show":"about_us_show"})


def TermsAndConditionsView(request):
    try:
        terms = Pages.objects.get(type_id=TERMS_AND_CONDITION)
    except:
        terms = None
    return render(request, "frontend/terms_conditions.html",{"terms":terms})


def PrivacyPolicy(request):
    try:
        privacy = Pages.objects.get(type_id=PRIVACY_POLICY)
    except:
        privacy = None
    return render(request, "frontend/privacy.html",{"privacy":privacy})
