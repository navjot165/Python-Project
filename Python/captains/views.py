import environ
from accounts.decorators import *
from accounts.utils import *
from .models import *
from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
env = environ.Env()
environ.Env.read_env()


@admins_only
@check_permissions('captains.plans_list')
def CaptainPlansList(request):
    plans = Plans.objects.all().order_by('-created_on')
    if request.GET.get('name'):
        plans = plans.filter(name__icontains = request.GET.get('name'))
    if request.GET.get('plan_type'):
        plans = plans.filter(plan_type = request.GET.get('plan_type'))
    if request.GET.get('shift_type'):
        plans = plans.filter(shift_type = request.GET.get('shift_type'))
    if request.GET.get('created_on'):
        plans = plans.filter(created_on__date = request.GET.get('created_on'))
    if request.GET and not plans:
        messages.error(request, 'No Data Found')
    return render(request, 'captain-plans/captain-plans-list.html', {
        "head_title":"Captain Plans Management",
        "plans": get_pagination(request, plans),
        "name":request.GET.get('name') if request.GET.get('name') else "",
        "plan_type":request.GET.get('plan_type') if request.GET.get('plan_type') else "",
        "shift_type":request.GET.get('shift_type') if request.GET.get('shift_type') else "",
        "created_on":request.GET.get('created_on') if request.GET.get('created_on') else ""
    })


@admins_only
@check_permissions('captains.add_plan')
def AddCaptainPlan(request):
    if request.method == 'POST':
        if Plans.objects.filter(name = request.POST.get('name')):
            messages.error(request, 'Plan with same name already exists.')
            return redirect('captains:add_captain_plan')
        else:
            plan = Plans.objects.create(
                name = request.POST.get('name'),
                description = request.POST.get('description'),
                plan_type = request.POST.get('plan_type'),
                shift_type = request.POST.get('shift_type'),
                created_by = request.user
            )
            messages.success(request, "Captain Plan Added Successfully!")
            return redirect('captains:view_captain_plan', id=plan.id)
    return render(request, 'captain-plans/add-captain-plan.html', {
        "head_title":"Captain Plans Management",
    })


@admins_only
@check_permissions('captains.edit_plan')
def EditCaptainPlan(request, id):
    plan = Plans.objects.get(id=id)
    if request.method == 'POST':
        if Plans.objects.filter(name = request.POST.get('name')).exclude(id=id):
            messages.error(request, 'Plan with same name already exists.')
            return redirect('captains:edit_captain_plan')
        else:
            plan.name = request.POST.get('name')
            plan.description = request.POST.get('description')
            plan.plan_type = request.POST.get('plan_type')
            plan.shift_type = request.POST.get('shift_type')
            plan.save()
            messages.success(request, "Captain Plan Updated Successfully!")
            return redirect('captains:view_captain_plan', id=plan.id)
    return render(request, 'captain-plans/edit-captain-plan.html', {
        "head_title":"Captain Plans Management",
        "currencies":Currencies.objects.all().order_by('name'),
        "plan":plan
    })


@admins_only
@check_permissions('captains.view_plan')
def ViewCaptainPlan(request, id):
    plan = Plans.objects.get(id=id)
    return render(request, 'captain-plans/view-captain-plan.html', {
        "head_title":"Captain Plans Management",
        "plan":plan
    })


@admins_only
@check_permissions('captains.delete_plan')
def DeleteCaptainPlan(request, id):
    plan = Plans.objects.get(id=id)
    if Captain.objects.filter(plan=plan):
        messages.error(request, "Plan is being used by some users, so can not be deleted at the moment.")
    else:
        plan.delete()
        messages.success(request, "Plan Deleted Successfully!")
    return redirect('captains:captain_plans_list')


@admins_only
@check_permissions('captains.companies_list')
def CompaniesList(request):
    companies = Companies.objects.all().order_by('-created_on')
    if request.GET.get('name'):
        companies = companies.filter(name__icontains = request.GET.get('name'))
    if request.GET.get('address'):
        companies = companies.filter(address__icontains = request.GET.get('address'))
    if request.GET.get('description'):
        companies = companies.filter(description__icontains = request.GET.get('description'))
    if request.GET.get('created_on'):
        companies = companies.filter(created_on__date = request.GET.get('created_on'))
    if request.GET and not companies:
        messages.error(request, 'No Data Found')
    return render(request, 'companies/companies-list.html', {
        "head_title":"Companies Management",
        "companies":get_pagination(request, companies),
        "name":request.GET.get('name') if request.GET.get('name') else "",
        "address":request.GET.get('address') if request.GET.get('address') else "",
        "description":request.GET.get('description') if request.GET.get('description') else "",
        "created_on":request.GET.get('created_on') if request.GET.get('created_on') else "",
    })


@admins_only
@check_permissions('captains.view_company')
def ViewCompany(request, id):
    company = Companies.objects.get(id=id)
    return render(request, 'companies/view-company.html', {
        "head_title":"Companies Management", 
        "company":company,
        "GOOGLE_PLACES_KEY":env('GOOGLE_PLACES_KEY')
    })


@admins_only
@check_permissions('captains.add_company')
def AddCompany(request):
    if request.method == 'POST':
        if Companies.objects.filter(name=request.POST.get('name')):
            messages.error(request, 'Comapny with same name already exists.')
            return redirect('captains:companies_list')
        else:
            company = Companies.objects.create(
                name = request.POST.get('name'),
                description = request.POST.get('description'),
                address = request.POST.get('address'),
                latitude = request.POST.get('latitude'),
                longitude = request.POST.get('longitude'),
                company_logo = request.FILES.get('company_logo'),
                created_by = request.user,
                company_type = request.POST.get('company_type'),
                payment_mode = request.POST.get('payment_mode'),
                bank_account_number = request.POST.get('bank_account_number') if request.POST.get('bank_account_number') else None,
                mobile_money_number = request.POST.get('mobile_money_number') if request.POST.get('mobile_money_number') else None,
            )
            company.company_poc.add(CompanyPOC.objects.create(
                full_name = request.POST.get('full_name1'),
                country_code = request.POST.get('country_code1'),
                mobile_no = request.POST.get('mobile_no1'),
                profile_pic = request.FILES.get('profile_pic1') if request.FILES.get('profile_pic1') else None,
            ))
            company.company_poc.add(CompanyPOC.objects.create(
                full_name = request.POST.get('full_name2'),
                country_code = request.POST.get('country_code2'),
                mobile_no = request.POST.get('mobile_no2'),
                profile_pic = request.FILES.get('profile_pic2') if request.FILES.get('profile_pic2') else None,
            ))
            messages.success(request, 'Company Added Successfully!')
            return redirect('captains:view_company', id=company.id)
    return render(request, 'companies/add-company.html',{
        "head_title":"Companies Management", 
        "GOOGLE_PLACES_KEY":env('GOOGLE_PLACES_KEY')
    })


@admins_only
@check_permissions('captains.edit_company')
def EditCompany(request,id):
    company = Companies.objects.get(id=id)
    if request.method == 'POST':
        if Companies.objects.filter(name=request.POST.get('name')).exclude(id=company.id):
            messages.error(request, 'Comapny with same name already exists.')
            return redirect('captains:companies_list')
        else:
            company.name = request.POST.get('name')
            company.description = request.POST.get('description')
            company.address = request.POST.get('address')
            company.latitude = request.POST.get('latitude')
            company.longitude = request.POST.get('longitude')
            company.company_type = request.POST.get('company_type')
            company.payment_mode = request.POST.get('payment_mode')
            company.bank_account_number = request.POST.get('bank_account_number') if request.POST.get('bank_account_number') else None
            company.mobile_money_number = request.POST.get('mobile_money_number') if request.POST.get('mobile_money_number') else None
            if request.FILES.get('company_logo'):
                company.company_logo = request.FILES.get('company_logo') 
            company.save()
            Companies.company_poc.through.objects.filter(companies=company).delete()
            first_poc = CompanyPOC.objects.create(
                full_name = request.POST.get('full_name1'),
                country_code = request.POST.get('country_code1'),
                mobile_no = request.POST.get('mobile_no1'),
            )
            if request.FILES.get('profile_pic1'):
                first_poc.profile_pic = request.FILES.get('profile_pic1')
                first_poc.save()
            company.company_poc.add(first_poc)
            second_poc = CompanyPOC.objects.create(
                full_name = request.POST.get('full_name2'),
                country_code = request.POST.get('country_code2'),
                mobile_no = request.POST.get('mobile_no2'),
            )
            if request.FILES.get('profile_pic2'):
                second_poc.profile_pic = request.FILES.get('profile_pic2')
                second_poc.save()
            company.company_poc.add(second_poc)
            messages.success(request, 'Company Updated Successfully!')
            return redirect('captains:view_company', id=company.id)
    return render(request, 'companies/edit-company.html',{
        "head_title":"Companies Management", 
        "GOOGLE_PLACES_KEY":env('GOOGLE_PLACES_KEY'),
        "company":company
    })


@admins_only
def EditCompanyData(request):
    if request.is_ajax():
        company = Companies.objects.get(id=request.GET.get('company_id'))
        return JsonResponse({
            "name": company.name,
            "description": company.description,
            "address": company.address,
            "latitude": company.latitude,
            "longitude": company.longitude,
        })


@admins_only
@check_permissions('captains.delete_company')
def DeleteCompany(request, id):
    company = Companies.objects.get(id=id)
    if Captain.objects.filter(company = company):
        messages.error(request, "Company is being assigned to some captains, so cannot be deleted at the moment.")
    else:
        company.delete()
        messages.success(request, "Company Deleted Successfully!")
    return redirect('captains:companies_list')


@admins_only
@check_permissions('captains.verify_unverify_captain')
def VerifyUnverifyProfile(request):
    if request.method == 'POST':
        user = User.objects.get(id=request.POST.get('user_id'))
        if user.is_profile_verified:
            user.is_profile_verified = False
            message = "Captain Profile Unverified Successfully!"
        else:
            user.is_profile_verified = True
            message = "Captain Profile Verified Successfully!"
        user.save()
        messages.success(request, message)
        return redirect('users:view_user', id=user.id)


@admins_only
@check_permissions('captains.add_captain')
def AddCaptain(request):
    if request.method == 'POST':
        user = User.objects.create(
            first_name = request.POST.get("first_name"),
            last_name = request.POST.get("last_name"),
            full_name = request.POST.get("first_name") + " " + request.POST.get("last_name") if request.POST.get("last_name") else request.POST.get("first_name"),
            email = request.POST.get("email"),
            mobile_no = request.POST.get("mobile_no"),
            country_code = request.POST.get("country_code"),
            password = make_password(request.POST.get("password")),
            role_id = CAPTAIN,
            gender = request.POST.get("gender"),
            temp_otp = TEMP_OTP,
            referral_code = GenerateReferralCode(),
            is_profile_verified = True,
            mpesa_number = request.POST.get('mpesa_number').strip() if request.POST.get('mpesa_number').strip() else None
        )
        try:
            wallet = UserWallet.objects.get(user=user)
        except:
            wallet = UserWallet.objects.create(user=user)
        if request.POST.get('mpesa_number').strip():
            wallet.mpesa_number = request.POST.get('mpesa_number').strip()
            wallet.save()
        captain = Captain.objects.create(
            user = user,
            years_of_experience = request.POST.get("years_of_experience"),
            driving_license_expiry_date = request.POST.get("driving_license_expiry_date")
        )
        if request.FILES.get('profile_pic'):
            user.profile_pic = request.FILES.get('profile_pic')
            user.save()
        if request.FILES.getlist('driving_license'):
            [captain.driving_license.add(Image.objects.create(upload=img, user=request.user)) for img in request.FILES.getlist('driving_license')]
        if request.FILES.getlist('govt_id_proof'):
            [captain.govt_id_proof.add(Image.objects.create(upload=img, user=request.user)) for img in request.FILES.getlist('govt_id_proof')]
        SendUserEmail(request,user,'EmailTemplates/CaptainPassword.html','Registration confirmation',request.POST.get("email"),"","","",request.POST.get("password"))
        messages.success(request, 'Captain Profile Created Successfully!')
        return redirect('users:view_user', id=user.id)
    return render(request, 'captains/add-captain.html', {"head_title":"Captains Management"})


@admins_only
@check_permissions('captains.edit_captain')
def EditCaptain(request,id):
    user = User.objects.get(id=id)
    captain = Captain.objects.get(user=user)
    if request.method == 'POST':
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.full_name = request.POST.get("first_name") + " " + request.POST.get("last_name") if request.POST.get("last_name") else request.POST.get("first_name")
        user.email = request.POST.get("email")
        user.mobile_no = request.POST.get("mobile_no")
        user.country_code = request.POST.get("country_code")
        try:
            wallet = UserWallet.objects.get(user=user)
        except:
            wallet = UserWallet.objects.create(user=user)
        if request.POST.get('mpesa_number').strip():
            user.mpesa_number = request.POST.get('mpesa_number').strip()
            wallet.mpesa_number = request.POST.get('mpesa_number').strip()
            wallet.save()
        if request.POST.get("password"):
            user.password = make_password(request.POST.get("password"))
        user.gender = request.POST.get("gender")
        captain.years_of_experience = request.POST.get("years_of_experience")
        captain.driving_license_expiry_date = request.POST.get("driving_license_expiry_date")
        if request.FILES.get('profile_pic'):
            user.profile_pic = request.FILES.get('profile_pic')
        user.save()
        captain.save()
        if request.FILES.getlist('driving_license'):
            [captain.driving_license.add(Image.objects.create(upload=img, user=request.user)) for img in request.FILES.getlist('driving_license')]
        if request.FILES.getlist('govt_id_proof'):
            [captain.govt_id_proof.add(Image.objects.create(upload=img, user=request.user)) for img in request.FILES.getlist('govt_id_proof')]
        messages.success(request, 'Captain Profile Updated Successfully!')
        return redirect('users:view_user', id=user.id)

    return render(request, 'captains/edit-captain.html', {
        "head_title":"Captains Management",
        "captain":captain,
        "user":user,
    })


@admins_only
@check_permissions('captains.assign_plan')
def AssignCaptainPlan(request, id):
    captain = Captain.objects.get(id=id)
    plans = Plans.objects.all().order_by('-created_on')
    if request.GET.get('name'):
        plans = plans.filter(name__icontains = request.GET.get('name'))
    if request.GET.get('plan_type'):
        plans = plans.filter(plan_type = request.GET.get('plan_type'))
    if request.GET.get('price'):
        plans = plans.filter(price = request.GET.get('price'))
    if request.GET.get('shift_type'):
        plans = plans.filter(shift_type = request.GET.get('shift_type'))
    if request.GET.get('no_of_rides'):
        plans = plans.filter(no_of_rides = request.GET.get('no_of_rides'))
    if request.GET.get('no_of_hours'):
        plans = plans.filter(no_of_hours = request.GET.get('no_of_hours'))
    if request.GET.get('no_of_kms'):
        plans = plans.filter(no_of_kms = request.GET.get('no_of_kms'))
    if request.GET and not plans:
        messages.error(request, 'No Data Found')
    if request.GET.get('plan_id'):
        captain.plan = Plans.objects.get(id=request.GET.get('plan_id'))
        captain.save()
        messages.success(request, 'Plan Assigned Successfully!')
        return redirect('users:view_user', id=captain.user.id)
    return render(request, 'captains/assign-plan.html',{
        "head_title":"Captains Management",
        "captain_plans":get_pagination(request,plans),
        "captain":captain,
        "name":request.GET.get('name') if request.GET.get('name') else "",
        "plan_type":request.GET.get('plan_type') if request.GET.get('plan_type') else "",
        "price":request.GET.get('price') if request.GET.get('price') else "",
        "shift_type":request.GET.get('shift_type') if request.GET.get('shift_type') else "",
        "no_of_rides":request.GET.get('no_of_rides') if request.GET.get('no_of_rides') else "",
        "no_of_hours":request.GET.get('no_of_hours') if request.GET.get('no_of_hours') else "",
        "no_of_kms":request.GET.get('no_of_kms') if request.GET.get('no_of_kms') else "",
    })


@admins_only
@check_permissions('captains.assign_company')
def AssignCompany(request, id):
    captain = Captain.objects.get(id=id)
    companies = Companies.objects.all().order_by('-created_on')
    if request.GET.get('name'):
        companies = companies.filter(name__icontains = request.GET.get('name'))
    if request.GET.get('address'):
        companies = companies.filter(address__icontains = request.GET.get('address'))
    if request.GET.get('description'):
        companies = companies.filter(description__icontains = request.GET.get('description'))
    if request.GET and not companies:
        messages.error(request, 'No Data Found')
    if request.GET.get('company_id'):
        captain.company = Companies.objects.get(id=request.GET.get('company_id'))
        captain.save()
        messages.success(request, 'Company Assigned Successfully!')
        return redirect('users:view_user', id=captain.user.id)
    return render(request, 'captains/assign-company.html',{
        "head_title":"Captains Management",
        "companies":get_pagination(request, companies),
        "captain":captain,
        "name":request.GET.get('name') if request.GET.get('name') else "",
        "address":request.GET.get('address') if request.GET.get('address') else "",
        "description":request.GET.get('description') if request.GET.get('description') else "",
    })


@admins_only
@check_permissions('captains.assign_bus')
def AssignBus(request, id):
    captain = Captain.objects.get(id=id)
    buses = Buses.objects.filter(is_active=True).order_by('created_on')

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
    if request.GET.get('is_ac'):
        buses = buses.filter(is_ac = request.GET.get('is_ac'))
    if request.GET.get('is_sacco'):
        buses = buses.filter(is_sacco = request.GET.get('is_sacco'))
    if request.GET.get('is_ev'):
        buses = buses.filter(is_ev = request.GET.get('is_ev'))
    if request.GET and not buses:
        messages.error(request, 'No Data Found')
    if request.GET.get('bus_id'):
        bus = Buses.objects.get(id=request.GET.get('bus_id'))
        if AssignedCaptainBuses.objects.filter(captain = captain):
            messages.success(request, 'Bus has been already assigned to this captain.')
        else:
            AssignedCaptainBuses.objects.create(bus = bus, captain = captain)
            messages.success(request, 'Bus Assigned Successfully!')
        return redirect('users:view_user', id=captain.user.id)
    return render(request, 'captains/assign-bus.html',{
        "head_title":"Captains Management",
        "captain":captain,
        "buses":get_pagination(request, buses),
        "plate_number":request.GET.get('plate_number') if request.GET.get('plate_number') else "",
        "bus_type":request.GET.get('bus_type') if request.GET.get('bus_type') else "",
        "manufacture_year":request.GET.get('manufacture_year') if request.GET.get('manufacture_year') else "",
        "capacity":request.GET.get('capacity') if request.GET.get('capacity') else "",
        "is_active":request.GET.get('is_active') if request.GET.get('is_active') else "",
        "is_ac":request.GET.get('is_ac') if request.GET.get('is_ac') else "",
        "is_sacco":request.GET.get('is_sacco') if request.GET.get('is_sacco') else "",
        "is_ev":request.GET.get('is_ev') if request.GET.get('is_ev') else "",
    })
