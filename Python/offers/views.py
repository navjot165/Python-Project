import logging
from accounts.decorators import *
from accounts.helper import *
from accounts.utils import *
from routes.models import *
from frontend.views import *
from django.contrib import messages
from django.shortcuts import render, redirect
db_logger = logging.getLogger('db')


@admins_only
@check_permissions('offers.offers_list')
def OffersList(request):
    offers = OfferCodes.objects.all().order_by('-created_on')
    if request.GET.get('name'):
        offers = offers.filter(name__icontains = request.GET.get('name'))
    if request.GET.get('route_name'):
        offers = offers.filter(routes__route_name__icontains = request.GET.get('route_name'))
    if request.GET.get('code'):
        offers = offers.filter(code__icontains = request.GET.get('code'))
    if request.GET.get('offer_type'):
        offers = offers.filter(offer_type = request.GET.get('offer_type'))
    if request.GET.get('promo_type'):
        offers = offers.filter(promo_type = request.GET.get('promo_type'))
    if request.GET.get('off_percentage'):
        offers = offers.filter(off_percentage__icontains = request.GET.get('off_percentage'))
    if request.GET.get('expiry_date'):
        offers = offers.filter(expiry_date = request.GET.get('expiry_date'))
    if request.GET.get('promo_status'):
        offers = offers.filter(promo_status = request.GET.get('promo_status'))
    if request.GET and not offers:
        messages.error(request, 'No Data Found')
    return render(request, 'offers/offer-list.html',{
        "offers":offers,
        "head_title":"Offers Management",
        "name": request.GET.get('name') if request.GET.get('name') else "",
        "route_name": request.GET.get('route_name') if request.GET.get('route_name') else "",
        "code": request.GET.get('code') if request.GET.get('code') else "",
        "offer_type": request.GET.get('offer_type') if request.GET.get('offer_type') else "",
        "promo_type": request.GET.get('promo_type') if request.GET.get('promo_type') else "",
        "off_percentage": request.GET.get('off_percentage') if request.GET.get('off_percentage') else "",
        "expiry_date": request.GET.get('expiry_date') if request.GET.get('expiry_date') else "",
        "promo_status": request.GET.get('promo_status') if request.GET.get('promo_status') else ""
    })


@admins_only
@check_permissions('offers.add_offer')
def AddOffer(request):
    if request.method == 'POST':
        offer = OfferCodes.objects.create(
            name = request.POST.get('name'),
            description = request.POST.get('description'),
            code = request.POST.get('code'),
            expiry_date = request.POST.get('expiry_date') if request.POST.get('expiry_date') else None,
            promo_type = PERCENTAGE_PROMO,
            off_percentage = request.POST.get('off_percentage') if request.POST.get('off_percentage') else None,
            created_by = request.user,
            offer_type = request.POST.get('offer_type'),
            max_usage_per_person = request.POST.get('max_usage_per_person'),
            maximum_price = request.POST.get('maximum_price')
        )
        [offer.routes.add(Routes.objects.get(id=route_id)) for route_id in request.POST.getlist('route')]
        active_codes = OfferCodes.objects.filter(promo_status=ACTIVE_PROMO, offer_type = request.POST.get('offer_type'))
        if request.POST.getlist('route'):
            active_codes = active_codes.filter(routes__id__in=request.POST.getlist('route'))
        offer.promo_status = INACTIVE_PROMO if active_codes else ACTIVE_PROMO
        offer.save()
        messages.success(request, 'Offer Added Successfully!')
        return redirect('offers:view_offer',id=offer.id)
    return render(request, 'offers/add-offer.html',{
        "head_title":"Offers Management",
        "routes":Routes.objects.filter(is_active=True)
    })


@admins_only
@check_permissions('offers.view_offer')
def ViewOffer(request, id):
    offer = OfferCodes.objects.get(id=id)
    offer_used = OfferCodeUsed.objects.filter(code=offer).order_by('-used_on')
    return render(request, 'offers/view-offer.html',{
        "head_title":"Offers Management",
        "offer":offer,
        "offer_used":get_pagination(request, offer_used)
    })


@admins_only
@check_permissions('offers.delete_offer')
def DeleteOffer(request, id):
    offer = OfferCodes.objects.get(id=id)
    if Booking.objects.filter(promo_used=offer):
        messages.error(request, 'Offer is being used in some bookings, so it cannot be deleted at the moment.')
        return redirect('offers:view_offer',id=offer.id)
    else:
        offer.delete()
        messages.success(request, 'Offer Deleted Successfully!')
        return redirect('offers:offers_list')


@admins_only 
@check_permissions('offers.edit_offer')
def EditOffer(request, id):
    offer = OfferCodes.objects.get(id=id)
    if Booking.objects.filter(promo_used=offer):
        messages.error(request, 'Offer is being used in some bookings, so it cannot be updated at the moment.')
        return redirect('offers:view_offer',id=offer.id)
    if request.method == 'POST':
        offer.name = request.POST.get('name')
        offer.description = request.POST.get('description')
        offer.code = request.POST.get('code')
        offer.expiry_date = request.POST.get('expiry_date') if request.POST.get('expiry_date') else None
        offer.promo_type = PERCENTAGE_PROMO
        offer.off_percentage = request.POST.get('off_percentage') if request.POST.get('off_percentage') else None
        offer.max_usage_per_person = request.POST.get('max_usage_per_person') if request.POST.get('max_usage_per_person') else None
        offer.maximum_price = request.POST.get('maximum_price')
        offer.save()
        OfferCodes.routes.through.objects.filter(offercodes_id=offer.id).delete()
        [offer.routes.add(Routes.objects.get(id=route_id)) for route_id in request.POST.getlist('route')]
        messages.success(request, 'Offer Updated Successfully!')
        return redirect('offers:view_offer',id=offer.id)
    routes_id = OfferCodes.routes.through.objects.filter(offercodes_id=offer.id).values_list('routes_id',flat=True)
    return render(request, 'offers/edit-offer.html',{
        "head_title":"Offers Management",
        "routes":Routes.objects.filter(is_active=True).exclude(id__in=routes_id),
        "offer":offer,
        "selected_routes":Routes.objects.filter(id__in=routes_id)
    })


@admins_only
@check_permissions('offers.activate_deactivate_offer')
def ActivateDeactivateOffer(request):
    if request.method == 'POST':
        offer = OfferCodes.objects.get(id=request.POST.get('offer_id'))
        if offer.promo_status == ACTIVE_PROMO:
            offer.promo_status = INACTIVE_PROMO
            messages.success(request, 'Offer Deactivated Successfully!')
        elif offer.promo_status == INACTIVE_PROMO:
            if offer.offer_type == OFFER_PROMO_TYPE:
                routes_id = OfferCodes.routes.through.objects.filter(offercodes_id=offer.id).values_list('routes_id',flat=True)
                OfferCodes.objects.filter(offer_type = offer.offer_type, routes__id__in=routes_id).exclude(id=offer.id).update(promo_status = INACTIVE_PROMO)
            else:
                OfferCodes.objects.filter(offer_type = offer.offer_type).exclude(id=offer.id).update(promo_status = INACTIVE_PROMO)
            offer.promo_status = ACTIVE_PROMO
            messages.success(request, 'Offer Activated Successfully!')
        offer.save()
        return redirect('offers:view_offer',id=offer.id) 