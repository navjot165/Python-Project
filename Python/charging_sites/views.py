import environ
from accounts.decorators import *
from accounts.utils import get_pagination
from .models import *
from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import JsonResponse
from datetime import datetime
env = environ.Env()
environ.Env.read_env()


@admins_only
@check_permissions('charging_sites.charging_sites_list')
def ChargingSitesList(request):
    charging_sites = ChargingSites.objects.all().order_by('-created_on')
    if request.GET.get('name'):
        charging_sites = charging_sites.filter(name__icontains=request.GET.get('name'))
    if request.GET.get('location'):
        charging_sites = charging_sites.filter(location__icontains=request.GET.get('location'))
    if request.GET.get('opening_time'):
        charging_sites = charging_sites.filter(opening_time=request.GET.get('opening_time'))
    if request.GET.get('closing_time'):
        charging_sites = charging_sites.filter(closing_time=request.GET.get('closing_time'))
    if request.GET.get('created_on'):
        charging_sites = charging_sites.filter(created_on__date=request.GET.get('created_on'))
    if request.GET and not charging_sites:
        messages.error(request, 'No Data Found')
    return render(request, 'charging-sites/charging-sites-list.html',{
        "charging_sites":get_pagination(request,charging_sites),
        "head_title":"Charging Sites Management",
        "name":request.GET.get('name') if request.GET.get('name') else "",
        "location":request.GET.get('location') if request.GET.get('location') else "",
        "opening_time":request.GET.get('opening_time') if request.GET.get('opening_time') else "",
        "closing_time":request.GET.get('closing_time') if request.GET.get('closing_time') else "",
        "created_on":request.GET.get('created_on') if request.GET.get('created_on') else "",
    })


@admins_only
@check_permissions('charging_sites.add_charging_site')
def AddChargingSite(request):
    if request.method == 'POST':
        if ChargingSites.objects.filter(location = request.POST.get('location'), latitude = request.POST.get('latitude'), longitude = request.POST.get('longitude')):
            messages.error(request, "Charging Site with same location already exists.")
            return redirect('charging_sites:add_charging_site')
        else:
            charging_site = ChargingSites.objects.create(
                name = request.POST.get('name'),
                charging_points_count = request.POST.get('charging_points_count'),
                capacity = request.POST.get('capacity'),
                location = request.POST.get('location'),
                latitude = request.POST.get('latitude'),
                longitude = request.POST.get('longitude'),
                opening_time = request.POST.get('opening_time'),
                closing_time = request.POST.get('closing_time'),
                created_by = request.user
            )
            messages.success(request, "Charging Site Added Successfully!")
            return redirect('charging_sites:view_charging_site', id=charging_site.id)
    return render(request, 'charging-sites/add-charging-site.html', {
        "head_title":"Charging Sites Management",
        "GOOGLE_PLACES_KEY":env('GOOGLE_PLACES_KEY')
    })


@admins_only
@check_permissions('charging_sites.edit_charging_site')
def EditChargingSite(request, id):
    charging_site = ChargingSites.objects.get(id=id)
    if request.method == 'POST':
        if ChargingSites.objects.filter(location = request.POST.get('location'), latitude = request.POST.get('latitude'), longitude = request.POST.get('longitude')).exclude(id=id):
            messages.error(request, "Charging Site with same location already exists.")
            return redirect('charging_sites:edit_charging_site')
        else:
            charging_site.name = request.POST.get('name')
            charging_site.charging_points_count = request.POST.get('charging_points_count')
            charging_site.capacity = request.POST.get('capacity')
            charging_site.location = request.POST.get('location')
            charging_site.latitude = request.POST.get('latitude')
            charging_site.longitude = request.POST.get('longitude')
            charging_site.opening_time = request.POST.get('opening_time')
            charging_site.closing_time = request.POST.get('closing_time')
            charging_site.save()
            messages.success(request, "Charging Site Updated Successfully!")
            return redirect('charging_sites:view_charging_site', id=charging_site.id)
    return render(request, 'charging-sites/edit-charging-site.html', {
        "head_title":"Charging Sites Management",
        "GOOGLE_PLACES_KEY":env('GOOGLE_PLACES_KEY'),
        "charging_site":charging_site
    })


@admins_only
@check_permissions('charging_sites.view_charging_site')
def ViewChargingSite(request, id):
    charging_site = ChargingSites.objects.get(id=id)
    return render(request, 'charging-sites/view-charging-site.html',{
        "head_title":"Charging Sites Management",
        "GOOGLE_PLACES_KEY":env('GOOGLE_PLACES_KEY'),
        "charging_site":charging_site
    })


@admins_only
@check_permissions('charging_sites.delete_charging_site')
def DeleteChargingSite(request, id):
    ChargingSites.objects.get(id=id).delete()
    messages.success(request, "Charging Site Deleted Successfully!")
    return redirect('charging_sites:charging_sites_list')


@admins_only
def CheckTimeValidations(request):
    if request.is_ajax():
        data = {'time_greater':False}
        opening_time = datetime.combine(datetime.now().date(), datetime.strptime(request.GET.get('opening_time'), '%H:%M').time())
        closing_time = datetime.combine(datetime.now().date(), datetime.strptime(request.GET.get('closing_time'), '%H:%M').time())
        if opening_time > closing_time:
            data['time_greater'] = True
        return JsonResponse(data)