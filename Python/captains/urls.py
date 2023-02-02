from django.contrib import admin
from .views import *
from django.urls import re_path


admin.autodiscover()
app_name = 'captains'


urlpatterns = [

    ## Captian Plans
    re_path(r'captain-plans-list/$',CaptainPlansList,name="captain_plans_list"),
    re_path(r'add-captain-plan/$',AddCaptainPlan,name="add_captain_plan"),
    re_path(r'view-captain-plan/(?P<id>[-\w]+)/$',ViewCaptainPlan,name="view_captain_plan"),
    re_path(r'edit-captain-plan/(?P<id>[-\w]+)/$',EditCaptainPlan,name="edit_captain_plan"),
    re_path(r'delete-captain-plan/(?P<id>[-\w]+)/$',DeleteCaptainPlan,name="delete_captain_plan"),

    ## Companies
    re_path(r'companies-list/$',CompaniesList,name="companies_list"),
    re_path(r'add-company/$',AddCompany,name="add_company"),
    re_path(r'edit-company/(?P<id>[-\w]+)/$',EditCompany,name="edit_company"),
    re_path(r'edit-company-data/$',EditCompanyData,name="edit_company_data"),
    re_path(r'view-company/(?P<id>[-\w]+)/$',ViewCompany,name="view_company"),
    re_path(r'delete-company/(?P<id>[-\w]+)/$',DeleteCompany,name="delete_company"),

    ## Captain
    re_path(r'verify-unverify-profile/$',VerifyUnverifyProfile,name="verify_unverify_profile"),
    re_path(r'add-captain/$',AddCaptain,name="add_captain"),
    re_path(r'edit-captain/(?P<id>[-\w]+)/$',EditCaptain,name="edit_captain"),
    re_path(r'assign-captain-plan/(?P<id>[-\w]+)/$',AssignCaptainPlan,name="assign_captain_plan"),
    re_path(r'assign-company/(?P<id>[-\w]+)/$',AssignCompany,name="assign_company"),
    re_path(r'assign-bus/(?P<id>[-\w]+)/$',AssignBus,name="assign_bus"),
    
]