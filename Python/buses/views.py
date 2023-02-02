from accounts.decorators import *
from contact_us.models import *
from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.utils import *
from django.http import JsonResponse
from .models import *


@admins_only
@check_permissions('buses.bus_type_list')
def BusTypesList(request):
    bus_types = BusTypes.objects.all().order_by('-created_on')
    if request.GET.get('name'):
        bus_types = bus_types.filter(name__icontains = request.GET.get('name'))
    if request.GET.get('description'):
        bus_types = bus_types.filter(description__icontains = request.GET.get('description'))
    if request.GET.get('seat_count'):
        bus_types = bus_types.filter(seat_count = request.GET.get('seat_count'))
    if request.GET.get('max_seat_count'):
        bus_types = bus_types.filter(max_seat_count = request.GET.get('max_seat_count'))
    if request.GET.get('created_on'):
        bus_types = bus_types.filter(created_on__date = request.GET.get('created_on'))
    
    if request.GET and not bus_types:
        messages.error(request, 'No Data Found')

    return render(request, "bus-types/bus-types-list.html",{
        "head_title":"Bus Types Management",
        "bus_types":get_pagination(request,bus_types),
        "name":request.GET.get('name') if request.GET.get('name') else "",
        "description":request.GET.get('description') if request.GET.get('description') else "",
        "seat_count":request.GET.get('seat_count') if request.GET.get('seat_count') else "",
        "max_seat_count":request.GET.get('max_seat_count') if request.GET.get('max_seat_count') else "",
        "created_on":request.GET.get('created_on') if request.GET.get('created_on') else "",
    })


@admins_only
@check_permissions('buses.add_bus_type')
def AddBusType(request):
    if request.method == 'POST':
        if BusTypes.objects.filter(name=request.POST.get('name')):
            messages.error(request, 'Bus Type with same name already exists!')
        else:
            bus_type = BusTypes.objects.create(
                name = request.POST.get('name').strip(),
                description = request.POST.get('description').strip(),
                seat_count = request.POST.get('seat_count'),
                max_seat_count = request.POST.get('max_seat_count'),
            )
            messages.success(request, 'Bus Type Added Successfully!')
            return redirect('buses:view_bus_type', bus_type.id)
    return render(request, 'bus-types/add-bus-type.html', {"head_title":"Bus Types Management"})


@admins_only
@check_permissions('buses.view_bus_type')
def ViewBusType(request, id):
    bus_type = BusTypes.objects.get(id=id)
    return render(request, 'bus-types/view-bus-type.html', {"head_title":"Bus Types Management","bus_type":bus_type})


@admins_only
@check_permissions('buses.delete_bus_type')
def DeleteBusType(request, id):
    bus_type = BusTypes.objects.get(id=id)
    if Buses.objects.filter(bus_type=bus_type):
        messages.error(request, "Bus Type is being used and cannot be deleted.")
    else:
        bus_type.delete()
        messages.success(request, 'Bus Type Deleted Successfully!')
    return redirect('buses:bus_types')


@admins_only
@check_permissions('buses.edit_bus_type')
def EditBusType(request, id):
    bus_type = BusTypes.objects.get(id=id)
    if request.method == 'POST':
        if BusTypes.objects.filter(name=request.POST.get('name')).exclude(id=id):
            messages.error(request, 'Bus Type with same name already exists!')
            return redirect('buses:bus_types')
        else:
            bus_type.name = request.POST.get('name').strip()
            bus_type.description = request.POST.get('description').strip() if request.POST.get('description') else ""
            bus_type.seat_count = request.POST.get('seat_count')
            bus_type.max_seat_count = request.POST.get('max_seat_count')
            bus_type.save()
            messages.success(request, 'Bus Type Updated Successfully!')
            return redirect('buses:view_bus_type', bus_type.id)
    return render(request, 'bus-types/edit-bus-type.html', {"head_title":"Bus Types Management","bus_type":bus_type})


@admins_only
@check_permissions('buses.bus_list')
def BusesList(request):
    buses = Buses.objects.all().order_by('-created_on')
    if request.GET.get('plate_number'):
        buses = buses.filter(plate_number__icontains = request.GET.get('plate_number'))
    if request.GET.get('bus_type'):
        buses = buses.filter(bus_type__name__icontains = request.GET.get('bus_type'))
    if request.GET.get('manufacture_year'):
        buses = buses.filter(manufacture_year = request.GET.get('manufacture_year'))
    if request.GET.get('capacity'):
        buses = buses.filter(bus_type__seat_count = request.GET.get('capacity'))
    if request.GET.get('is_active'):
        buses = buses.filter(is_active = request.GET.get('is_active'))
    if request.GET.get('created_on'):
        buses = buses.filter(created_on__date = request.GET.get('created_on'))
    
    if request.GET and not buses:
        messages.error(request, 'No Data Found')

    return render(request, "buses/buses-list.html",{
        "head_title":"Buses Management",
        "buses":get_pagination(request,buses),
        "plate_number":request.GET.get('plate_number') if request.GET.get('plate_number') else "",
        "bus_type":request.GET.get('bus_type') if request.GET.get('bus_type') else "",
        "manufacture_year":request.GET.get('manufacture_year') if request.GET.get('manufacture_year') else "",
        "capacity":request.GET.get('capacity') if request.GET.get('capacity') else "",
        "is_active":request.GET.get('is_active') if request.GET.get('is_active') else "",
        "created_on":request.GET.get('created_on') if request.GET.get('created_on') else "",
    })


@admins_only
@check_permissions('buses.add_bus')
def AddBus(request):
    if request.method == 'POST':
        if Buses.objects.filter(plate_number=request.POST.get('plate_number')):
            messages.error(request, 'Bus with same plate number already exists!')
            return redirect('buses:add_bus_type')
        else:
            bus = Buses.objects.create(
                plate_number = request.POST.get('plate_number').strip(),
                manufacture_year = request.POST.get('manufacture_year'),
                bus_type = BusTypes.objects.get(id=request.POST.get('bus_type')),
                is_ac = request.POST.get('is_ac'),
                is_sacco = request.POST.get('is_sacco'),
                is_ev = request.POST.get('is_ev'),
                is_regular = request.POST.get('is_regular'),
                description = request.POST.get('description').strip() if request.POST.get('description') else "",
                is_active = True
            )
            if request.FILES.getlist('vehicle_image'):
                [bus.vehicle_image.add(Image.objects.create(upload=img)) for img in request.FILES.getlist('vehicle_image')]
            if request.FILES.getlist('ownership_document'):
                [bus.ownership_document.add(Image.objects.create(upload=img)) for img in request.FILES.getlist('ownership_document')]
            messages.success(request, 'Bus Added Successfully!')    
            return redirect('buses:view_bus',id=bus.id)
    return render(request, 'buses/add-bus.html',{
        "head_title":"Buses Management",
        "bus_types":BusTypes.objects.all().order_by('-created_on')
    })


@admins_only
@check_permissions('buses.view_bus')
def ViewBus(request, id):
    bus = Buses.objects.get(id=id)
    assigned_captains = AssignedCaptainBuses.objects.filter(bus=bus).values_list('captain__user_id', flat=True).order_by('-assigned_on')
    assigned_captains = User.objects.filter(id__in=assigned_captains).order_by('-created_on')

    if request.GET.get('full_name'):
        assigned_captains = assigned_captains.filter(full_name__icontains = request.GET.get('full_name'))
    if request.GET.get('email'):
        assigned_captains = assigned_captains.filter(email__icontains = request.GET.get('email'))
    if request.GET.get('mobile_no'):
        assigned_captains = assigned_captains.filter(mobile_no__icontains = request.GET.get('mobile_no'))
    if request.GET.get('is_profile_verified'):
        assigned_captains = assigned_captains.filter(is_profile_verified = request.GET.get('is_profile_verified'))
    if request.GET.get('status'):
        assigned_captains = assigned_captains.filter(status=request.GET.get('status'))
    return render(request, 'buses/view-bus.html', {
        "head_title":"Buses Management","bus":bus,"assigned_captains":get_pagination(request, assigned_captains),
        "full_name":request.GET.get('full_name') if request.GET.get('full_name') else "",
        "email":request.GET.get('email') if request.GET.get('email') else "",
        "mobile_no":request.GET.get('mobile_no') if request.GET.get('mobile_no') else "",
        "status":request.GET.get('status') if request.GET.get('status') else "",
        "is_profile_verified":request.GET.get('is_profile_verified') if request.GET.get('is_profile_verified') else "",
    })


@admins_only
@check_permissions('buses.delete_bus')
def DeleteBus(request, id):
    Buses.objects.get(id=id).delete()
    messages.success(request, "Bus Deleted Successfully!")
    return redirect('buses:buses_list')


@admins_only
@check_permissions('buses.edit_bus')
def EditBus(request, id):
    bus = Buses.objects.get(id=id)
    if request.method == 'POST':
        if Buses.objects.filter(plate_number=request.POST.get('plate_number')).exclude(id=id):
            messages.error(request, 'Bus with same plate number already exists!')
            return redirect('buses:add_bus_type')
        else:
            bus.plate_number = request.POST.get('plate_number').strip()
            bus.manufacture_year = request.POST.get('manufacture_year')
            bus.bus_type = BusTypes.objects.get(id=request.POST.get('bus_type'))
            bus.is_ac = request.POST.get('is_ac')
            bus.is_sacco = request.POST.get('is_sacco')
            bus.is_ev = request.POST.get('is_ev')
            bus.is_regular = request.POST.get('is_regular')
            bus.description = request.POST.get('description').strip() if request.POST.get('description') else ""
            bus.save()
            if request.FILES.getlist('vehicle_image'):
                Buses.vehicle_image.through.objects.filter(buses_id=id).delete()
                [bus.vehicle_image.add(Image.objects.create(upload=img)) for img in request.FILES.getlist('vehicle_image')]
            if request.FILES.getlist('ownership_document'):
                Buses.ownership_document.through.objects.filter(buses_id=id).delete()
                [bus.ownership_document.add(Image.objects.create(upload=img)) for img in request.FILES.getlist('ownership_document')]
            messages.success(request, 'Bus Updated Successfully!')    
            return redirect('buses:view_bus',id=bus.id)
    return render(request, 'buses/edit-bus.html', {"head_title":"Buses Management", "bus":bus,"bus_types":BusTypes.objects.all().order_by('-created_on')})


@admins_only
def BusValidations(request):
    if request.is_ajax():
        data = {}
        bus_exist = Buses.objects.filter(plate_number=request.GET.get('plate_number'))
        if request.GET.get('bus_id'):
            bus_exist = bus_exist.exclude(id=request.GET.get('bus_id'))
        if bus_exist:
            data['exists'] = '1'
        else:
            data['exists'] = '0'
        return JsonResponse(data)


@admins_only
@check_permissions('buses.activate_deactivate_bus')
def ActivateDeactivateBus(request):
    if request.method == 'POST':
        bus = Buses.objects.get(id=request.POST.get('bus_id'))
        if bus.is_active:
            bus.is_active = False 
            bus.save()
            messages.success(request, "Bus Deactivated Successfull!")
        else:
            bus.is_active = True
            bus.save()
            messages.success(request, "Bus Activated Successfully!")
        return redirect('buses:view_bus', id=bus.id)