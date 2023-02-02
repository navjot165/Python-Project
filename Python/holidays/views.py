import environ
import logging
from accounts.decorators import *
from accounts.helper import *
from accounts.utils import *
from routes.models import *
from frontend.views import *
from django.contrib import messages
from django.shortcuts import render, redirect
env = environ.Env()
environ.Env.read_env()
db_logger = logging.getLogger('db')


@admins_only
@check_permissions('holidays.category_list')
def RouteCategoriesList(request):
    categories = Category.objects.all().order_by('-created_on')
    if request.GET.get('name'):
        categories = categories.filter(name__icontains = request.GET.get('name'))
    if request.GET.get('description'):
        categories = categories.filter(description__icontains = request.GET.get('description'))
    if request.GET.get('base_fare'):
        categories = categories.filter(base_fare = request.GET.get('base_fare'))
    if request.GET.get('max_fare'):
        categories = categories.filter(max_fare = request.GET.get('max_fare'))
    if request.GET.get('base_distance'):
        categories = categories.filter(base_distance = request.GET.get('base_distance'))
    if request.GET.get('flags'):
        categories = categories.filter(flags = request.GET.get('flags'))
    if request.GET.get('category_type'):
        categories = categories.filter(category_type = request.GET.get('category_type'))
    if request.GET.get('created_on'):
        categories = categories.filter(created_on__date = request.GET.get('created_on'))
    categories = get_pagination(request, categories)
    if request.GET and not categories:
        messages.error(request, 'No Data Found')
    return render(request, 'categories/categories-list.html', {
        "head_title":"Categories Management", 
        "categories":categories,
        "GOOGLE_PLACES_KEY":env('GOOGLE_PLACES_KEY'),
        "name": request.GET.get('name') if request.GET.get('name') else "",
        "description": request.GET.get('description') if request.GET.get('description') else "",
        "base_fare": request.GET.get('base_fare') if request.GET.get('base_fare') else "",
        "max_fare": request.GET.get('max_fare') if request.GET.get('max_fare') else "",
        "base_distance": request.GET.get('base_distance') if request.GET.get('base_distance') else "",
        "flags": int(request.GET.get('flags') if request.GET.get('flags') else 0),
        "category_type": int(request.GET.get('category_type') if request.GET.get('category_type') else 0),
        "created_on": request.GET.get('created_on') if request.GET.get('created_on') else "",
    })


@admins_only
@check_permissions('holidays.add_category')
def AddRouteCategory(request):
    if request.method == 'POST':
        if Category.objects.filter(name=request.POST.get('name')):
            messages.error(request, "Category with same name already exist.")
            return redirect('holidays:add_route_category')
        else:
            category = Category.objects.create(
                name = request.POST.get('name'),
                description = request.POST.get('description'),
                max_seats_per_person = request.POST.get('max_seats_per_person'),
                base_fare = request.POST.get('base_fare'),
                max_fare = request.POST.get('max_fare'),
                base_distance = request.POST.get('base_distance'),
                distance_bucket_size = request.POST.get('distance_bucket_size'),
                distance_bucket_fare = request.POST.get('distance_bucket_fare'),
                time_bucket_size = request.POST.get('time_bucket_size'),
                time_bucket_fare = request.POST.get('time_bucket_fare'),
                flags = request.POST.get('flags'),
                category_type = request.POST.get('category_type'),
                arrival_allowance = request.POST.get('arrival_allowance'),
                departure_allowance = request.POST.get('departure_allowance'),
                created_by = request.user
            )
            messages.success(request, "Category Added Successfully!")
            return redirect('holidays:view_route_category', id=category.id)
    return render(request, 'categories/add-category.html', {"head_title":"Categories Management"})


@admins_only
@check_permissions('holidays.view_category')
def ViewRouteCategory(request, id):
    category = Category.objects.get(id=id)
    return render(request, 'categories/view-category.html', {"head_title":"Categories Management", "category":category})


@admins_only
@check_permissions('holidays.delete_category')
def DeleteRouteCategory(request, id):
    category = Category.objects.get(id=id)
    category.delete()
    messages.success(request, 'Category Deleted Successfully!')
    return redirect('holidays:route_categories_list')


@admins_only
@check_permissions('holidays.edit_category')
def EditRouteCategory(request, id):
    category = Category.objects.get(id=id)
    if request.method == 'POST':
        if Category.objects.filter(name=request.POST.get('name')).exclude(id=id):
            messages.error(request, "Category with same name already exist.")
            return redirect('holidays:edit_route_category', id = category.id)
        else:
            category.name = request.POST.get('name')
            category.description = request.POST.get('description')
            category.base_fare = request.POST.get('base_fare')
            category.max_fare = request.POST.get('max_fare')
            category.base_distance = request.POST.get('base_distance')
            category.max_seats_per_person = request.POST.get('max_seats_per_person')
            category.distance_bucket_size = request.POST.get('distance_bucket_size')
            category.distance_bucket_fare = request.POST.get('distance_bucket_fare')
            category.time_bucket_size = request.POST.get('time_bucket_size')
            category.time_bucket_fare = request.POST.get('time_bucket_fare')
            category.category_type = request.POST.get('category_type')
            category.flags = request.POST.get('flags')
            category.arrival_allowance = request.POST.get('arrival_allowance')
            category.departure_allowance = request.POST.get('departure_allowance')
            category.save()
            messages.success(request, "Category Updated Successfully!")
            UpdateCategorySchedules(category)
            return redirect('holidays:view_route_category', id=category.id)
    return render(request, 'categories/edit-category.html', {"head_title":"Categories Management", "category":category})


@admins_only
@check_permissions('holidays.holidays_list')
def HolidaysList(request):
    holidays = Holidays.objects.all().order_by('-created_on')
    if request.GET and not holidays:
        messages.error(request, 'No Data Found')
    return render(request, 'holidays/holidays-list.html', {
        "head_title":"Holidays Management",
        "holidays":get_pagination(request, holidays)
    })


@admins_only
@check_permissions('holidays.add_holiday')
def AddHoliday(request):
    if request.method == 'POST':
        if Holidays.objects.filter(holiday_date=request.POST.get('holiday_date')):
            messages.error(request, 'Holiday with same date already exists.')
        else:
            holiday = Holidays.objects.create(
                name = request.POST.get('name'),
                description = request.POST.get('description'),
                holiday_date = request.POST.get('holiday_date'),
                category = Category.objects.get(id=request.POST.get('category')),
                created_by = request.user
            )
            messages.success(request, 'Holiday Added Successfully!')
            return redirect('holidays:view_holiday',id=holiday.id)
    return render(request, 'holidays/add-holiday.html', {
        "head_title":"Holidays Management",
        "categories":Category.objects.all().order_by('-created_on')
    })


@admins_only
@check_permissions('holidays.edit_holiday')
def EditHoliday(request,id):
    holiday = Holidays.objects.get(id=id)
    if request.method == 'POST':
        if Holidays.objects.filter(holiday_date=request.POST.get('holiday_date')).exclude(id=id):
            messages.error(request, 'Holiday with same date already exists.')
            return redirect('holidays:edit_holidays',id=id)
        else:
            holiday.name = request.POST.get('name')
            holiday.description = request.POST.get('description')
            holiday.category = Category.objects.get(id=request.POST.get('category'))
            holiday.save()
            messages.success(request, 'Holiday Updated Successfully!')
            return redirect('holidays:view_holiday',id=holiday.id)
    return render(request, 'holidays/edit-holiday.html', {
        "head_title":"Holidays Management",
        "categories":Category.objects.all().order_by('-created_on'),
        "holiday":holiday
    })


@admins_only
@check_permissions('holidays.view_holiday')
def ViewHoliday(request, id):
    holiday = Holidays.objects.get(id=id)
    return render(request, 'holidays/view-holiday.html',{"head_title":"Holidays Management","holiday":holiday})


@admins_only
@check_permissions('holidays.delete_holiday')
def DeleteHoliday(request, id):
    Holidays.objects.get(id=id).delete()
    messages.success(request, 'Holiday Deleted Successfully!')
    return redirect('holidays:holidays_list')


def UpdateCategorySchedules(category):
    Schedules.objects.filter(category = category).update(
        arrival_allowance = category.arrival_allowance,
        departure_allowance = category.departure_allowance,
        base_fare = category.base_fare,
        max_fare = category.max_fare,
        max_seats_per_person = category.max_seats_per_person,
        base_distance = category.base_distance,
        distance_bucket_size = category.distance_bucket_size,
        distance_bucket_fare = category.distance_bucket_fare,
        time_bucket_size = category.time_bucket_size,
        time_bucket_fare = category.time_bucket_fare,
        category_type = category.category_type,
        flags = category.flags
    )
    