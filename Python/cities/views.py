import environ
from accounts.decorators import *
from accounts.utils import get_pagination
from accounts.models import *
from django.contrib import messages
from django.shortcuts import redirect, render

env = environ.Env()
environ.Env.read_env()


@admins_only
@check_permissions('accounts.countries_list')
def CountriesList(request):
    countries = Countries.objects.all().order_by('-created_on')
    if request.GET.get('name'):
        countries = countries.filter(name__icontains=request.GET.get('name'))
    if request.GET.get('initials'):
        countries = countries.filter(initials__icontains=request.GET.get('initials'))
    if request.GET.get('region'):
        countries = countries.filter(region__icontains=request.GET.get('region'))
    if request.GET.get('currency'):
        countries = countries.filter(currency__name__icontains=request.GET.get('currency'))
    if request.GET.get('created_on'):
        countries = countries.filter(created_on__date=request.GET.get('created_on'))
    if request.GET.get('default'):
        countries = countries.filter(default=request.GET.get('default'))
    if request.GET and not countries:
        messages.error(request, 'No Data Found')
    return render(request, 'countries/countries.html',{
        "countries":get_pagination(request,countries),
        "head_title":"Countries Management",
        "name":request.GET.get('name') if request.GET.get('name') else "",
        "initials":request.GET.get('initials') if request.GET.get('initials') else "",
        "region":request.GET.get('region') if request.GET.get('region') else "",
        "currency":request.GET.get('currency') if request.GET.get('currency') else "",
        "created_on":request.GET.get('created_on') if request.GET.get('created_on') else "",
        "default":request.GET.get('default') if request.GET.get('default') else "",
    })


@admins_only
@check_permissions('accounts.add_country')
def AddCountry(request):
    if request.method == 'POST':
        if Countries.objects.filter(name=request.POST.get('name'),latitude=request.POST.get('latitude'),longitude=request.POST.get('longitude')):
            messages.error(request, 'Country with same name already exists.')
            return redirect('cities:countries_list')
        else:
            country = Countries.objects.create(
                name = request.POST.get('name'),
                initials = request.POST.get('initials'),
                region = request.POST.get('region'),
                latitude = request.POST.get('latitude'),
                longitude = request.POST.get('longitude'),
                created_by = request.user,
                currency = Currencies.objects.get(id=request.POST.get('currency'))
            )
            messages.success(request, 'Country Added Successfully!')
            return redirect('cities:view_country', id=country.id)
    return render(request, 'countries/add-country.html',{
        "currencies":Currencies.objects.all().order_by('name'),
        "head_title":"Countries Management",
        "GOOGLE_PLACES_KEY":env('GOOGLE_PLACES_KEY')
    })


@admins_only
@check_permissions('accounts.edit_country')
def EditCountry(request,id):
    country = Countries.objects.get(id=id)
    if request.method == 'POST':
        if Countries.objects.filter(name=request.POST.get('name'),latitude=request.POST.get('latitude'),longitude=request.POST.get('longitude')).exclude(id=country.id):
            messages.error(request, 'Country with same name already exists.')
            return redirect('cities:countries_list')
        else:
            country.name = request.POST.get('name')
            country.initials = request.POST.get('initials')
            country.region = request.POST.get('region')
            country.latitude = request.POST.get('latitude')
            country.longitude = request.POST.get('longitude')
            country.currency = Currencies.objects.get(id=request.POST.get('currency'))
            country.save()
            messages.success(request, 'Country Updated Successfully!')
        return redirect('cities:view_country', id=country.id)
    return render(request, 'countries/edit-country.html',{
        "currencies":Currencies.objects.all().order_by('name'),
        "head_title":"Countries Management",
        "GOOGLE_PLACES_KEY":env('GOOGLE_PLACES_KEY'),
        "country":country
    })


@admins_only
@check_permissions('accounts.delete_country')
def DeleteCountry(request,id):
    country = Countries.objects.get(id=id)
    if Cities.objects.filter(country=country):
        messages.error(request, 'Country is being used in some cities so cannot be deleted at the moment.')
    else:
        country.delete()
        messages.success(request, "Country Deleted Successfully!")
    return redirect('cities:countries_list')


@admins_only
@check_permissions('accounts.view_country')
def ViewCountry(request, id):
    country = Countries.objects.get(id=id)
    return render(request, 'countries/view-country.html',{"country":country,"head_title":"Countries Management","GOOGLE_PLACES_KEY":env('GOOGLE_PLACES_KEY')})


@admins_only
@check_permissions('accounts.cities_list')
def CitiesList(request):
    cities = Cities.objects.all().order_by('-created_on')
    if request.GET.get('name'):
        cities = cities.filter(name__icontains=request.GET.get('name'))
    if request.GET.get('initials'):
        cities = cities.filter(initials__icontains=request.GET.get('initials'))
    if request.GET.get('country'):
        cities = cities.filter(country__name__icontains=request.GET.get('country'))
    if request.GET.get('latitude'):
        cities = cities.filter(latitude__icontains=request.GET.get('latitude'))
    if request.GET.get('longitude'):
        cities = cities.filter(longitude__icontains=request.GET.get('longitude'))
    if request.GET.get('created_on'):
        cities = cities.filter(created_on__date=request.GET.get('created_on'))
    if request.GET.get('default'):
        cities = cities.filter(default=request.GET.get('default'))
    if request.GET and not cities:
        messages.error(request, 'No Data Found')
    return render(request, 'cities/cities.html',{
        "countries":Countries.objects.all(),
        "cities":get_pagination(request,cities),
        "GOOGLE_PLACES_KEY":env('GOOGLE_PLACES_KEY'),
        "head_title":"Cities Management",
        "name":request.GET.get('name') if request.GET.get('name') else "",
        "initials":request.GET.get('initials') if request.GET.get('initials') else "",
        "country":request.GET.get('country') if request.GET.get('country') else "",
        "latitude":request.GET.get('latitude') if request.GET.get('latitude') else "",
        "longitude":request.GET.get('longitude') if request.GET.get('longitude') else "",
        "created_on":request.GET.get('created_on') if request.GET.get('created_on') else "",
        "default":request.GET.get('default') if request.GET.get('default') else "",
    })


@admins_only
@check_permissions('accounts.view_city')
def ViewCity(request, id):
    city = Cities.objects.get(id=id)
    return render(request, 'cities/view-city.html',{"city":city,"head_title":"Cities Management","GOOGLE_PLACES_KEY":env('GOOGLE_PLACES_KEY')})


@admins_only
@check_permissions('accounts.add_city')
def AddCity(request):
    if request.method == 'POST':
        country = Countries.objects.get(id=request.POST.get('country'))
        if Cities.objects.filter(name=request.POST.get('name'),latitude=request.POST.get('latitude'),longitude=request.POST.get('longitude'),country=country):
            messages.error(request, 'City with same name and country already exists.')
            return redirect('cities:cities_list')
        else:
            city = Cities.objects.create(
                name = request.POST.get('name'),
                initials = request.POST.get('initials'),
                country = country,
                latitude = request.POST.get('latitude'),
                longitude = request.POST.get('longitude'),
                created_by = request.user
            )
            messages.success(request, 'City Added Successfully!')
            return redirect('cities:view_city', id=city.id)
    return render(request, 'cities/add-city.html', {
        "countries":Countries.objects.all(),
        "GOOGLE_PLACES_KEY":env('GOOGLE_PLACES_KEY'),
        "head_title":"Cities Management",
    })


@admins_only
@check_permissions('accounts.delete_city')
def DeleteCity(request,id):
    city = Cities.objects.get(id=id)
    if District.objects.filter(city=city):
        messages.error(request, 'City is being used in some districts so cannot be deleted at the moment.')
    else:
        city.delete()
        messages.success(request, "City Deleted Successfully!")
    return redirect('cities:cities_list')


@admins_only
@check_permissions('accounts.edit_city')
def EditCity(request, id):
    city = Cities.objects.get(id=id)
    if request.method == 'POST':
        country = Countries.objects.get(id=request.POST.get('country'))
        if Cities.objects.filter(name=request.POST.get('name'),latitude=request.POST.get('latitude'),longitude=request.POST.get('longitude'),country=country).exclude(id=city.id):
            messages.error(request, 'City with same name and country already exists.')
            return redirect('cities:cities_list')
        else:
            city.name = request.POST.get('name')
            city.initials = request.POST.get('initials')
            city.country = country
            city.latitude = request.POST.get('latitude')
            city.longitude = request.POST.get('longitude')
            city.save()
            messages.success(request, 'City Updated Successfully!')
        return redirect('cities:view_city', id=city.id)
    return render(request, 'cities/edit-city.html', {
        "countries":Countries.objects.all(),
        "GOOGLE_PLACES_KEY":env('GOOGLE_PLACES_KEY'),
        "head_title":"Cities Management",
        "city":city
    })


@admins_only
@check_permissions('accounts.districts_list')
def DistrictsList(request):
    districts = District.objects.all().order_by('-created_on')
    if request.GET.get('name'):
        districts = districts.filter(name__icontains=request.GET.get('name'))
    if request.GET.get('initials'):
        districts = districts.filter(initials__icontains=request.GET.get('initials'))
    if request.GET.get('city'):
        districts = districts.filter(city__icontains=request.GET.get('city'))
    if request.GET.get('latitude'):
        districts = districts.filter(latitude__icontains=request.GET.get('latitude'))
    if request.GET.get('longitude'):
        districts = districts.filter(longitude__icontains=request.GET.get('longitude'))
    if request.GET.get('created_on'):
        districts = districts.filter(created_on__date=request.GET.get('created_on'))
    if request.GET and not districts:
        messages.error(request, 'No Data Found')
    return render(request, 'districts/districts.html',{
        "cities":Cities.objects.all(),
        "GOOGLE_PLACES_KEY":env('GOOGLE_PLACES_KEY'),
        "districts":get_pagination(request,districts),
        "head_title":"Districts Management",
        "name":request.GET.get('name') if request.GET.get('name') else "",
        "initials":request.GET.get('initials') if request.GET.get('initials') else "",
        "city":request.GET.get('city') if request.GET.get('city') else "",
        "latitude":request.GET.get('latitude') if request.GET.get('latitude') else "",
        "longitude":request.GET.get('longitude') if request.GET.get('longitude') else "",
        "created_on":request.GET.get('created_on') if request.GET.get('created_on') else "",
    })


@admins_only
@check_permissions('accounts.view_district')
def ViewDistrict(request, id):
    district = District.objects.get(id=id)
    return render(request, 'districts/view-district.html',{"district":district,"head_title":"Districts Management","GOOGLE_PLACES_KEY":env('GOOGLE_PLACES_KEY')})


@admins_only
@check_permissions('accounts.add_district')
def AddDistrict(request):
    if request.method == 'POST':
        city = Cities.objects.get(id=request.POST.get('city'))
        if District.objects.filter(name=request.POST.get('name'),latitude=request.POST.get('latitude'),longitude=request.POST.get('longitude'),city=city):
            messages.error(request, 'District with same name and city already exists.')
            return redirect('cities:districts_list')
        else:
            district = District.objects.create(
                name = request.POST.get('name'),
                initials = request.POST.get('initials'),
                city = city,
                latitude = request.POST.get('latitude'),
                longitude = request.POST.get('longitude'),
                created_by = request.user
            )
            messages.success(request, 'District Added Successfully!')
            return redirect('cities:view_district', id=district.id)

    return render(request, 'districts/add-district.html',{
        "cities":Cities.objects.all(),
        "GOOGLE_PLACES_KEY":env('GOOGLE_PLACES_KEY'),
        "head_title":"Districts Management",
    })


@admins_only
@check_permissions('accounts.edit_district')
def EditDistrict(request,id):
    district = District.objects.get(id=id)
    if request.method == 'POST':
        city = Cities.objects.get(id=request.POST.get('city'))
        if District.objects.filter(name=request.POST.get('name'),latitude=request.POST.get('latitude'),longitude=request.POST.get('longitude'),city=city).exclude(id=district.id):
            messages.error(request, 'District with same name and city already exists.')
            return redirect('cities:districts_list')
        else:
            district.name = request.POST.get('name')
            district.initials = request.POST.get('initials')
            district.city = city
            district.latitude = request.POST.get('latitude')
            district.longitude = request.POST.get('longitude')
            district.save()
            messages.success(request, 'District Updated Successfully!')
            return redirect('cities:view_district', id=district.id)

    return render(request, 'districts/edit-district.html',{
        "cities":Cities.objects.all(),
        "GOOGLE_PLACES_KEY":env('GOOGLE_PLACES_KEY'),
        "head_title":"Districts Management",
        "district":district
    })



@admins_only
@check_permissions('accounts.delete_district')
def DeleteDistrict(request,id):
    District.objects.get(id=id).delete()
    messages.success(request, "District Deleted Successfully!")
    return redirect('cities:districts_list')


@admins_only
@check_permissions('accounts.currencies_list')
def CurrenciesList(request):
    currencies = Currencies.objects.all().order_by('name')
    if request.GET.get('name'):
        currencies = currencies.filter(name__icontains=request.GET.get('name'))
    if request.GET.get('code'):
        currencies = currencies.filter(code__icontains=request.GET.get('code'))
    if request.GET.get('symbol'):
        currencies = currencies.filter(symbol=request.GET.get('symbol'))
    if request.GET and not currencies:
        messages.error(request, 'No Data Found')
    return render(request, 'admin/currencies.html',{
        "currencies":get_pagination(request,currencies),
        "head_title":"Currencies Management",
        "GOOGLE_PLACES_KEY":env('GOOGLE_PLACES_KEY'),
        "name":request.GET.get('name') if request.GET.get('name') else "",
        "code":request.GET.get('code') if request.GET.get('code') else "",
        "symbol":request.GET.get('symbol') if request.GET.get('symbol') else ""
    })


@admins_only
@check_permissions('accounts.delete_currency')
def DeleteCurrency(request,id):
    currency = Currencies.objects.get(id=id)
    if Countries.objects.filter(currency=currency):
        messages.error(request, "Currency is being used in some countries so cannot be deleted at the moment.")
    else:
        currency.delete()
        messages.success(request, "Currency Deleted Successfully!")
    return redirect('cities:currencies_list') 
    
    
    
    