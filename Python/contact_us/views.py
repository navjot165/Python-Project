from accounts.decorators import *
from contact_us.models import *
from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.utils import *


@admins_only
@check_permissions('contact_us.contact_us_list')
def ContactUsList(request):
    contacts = ContactUs.objects.all().order_by('-created_on')
    if request.GET.get('full_name'):
        contacts = contacts.filter(full_name__icontains = request.GET.get('full_name'))
    if request.GET.get('email'):
        contacts = contacts.filter(email__icontains = request.GET.get('email'))
    if request.GET.get('mobile_no'):
        contacts = contacts.filter(mobile_no__icontains = request.GET.get('mobile_no'))
    if request.GET.get('message'):
        contacts = contacts.filter(message__icontains = request.GET.get('message'))
    if request.GET.get('user'):
        contacts = contacts.filter(user__full_name__icontains = request.GET.get('user'))
    if request.GET.get('created_on'):
        contacts = contacts.filter(created_on__date = request.GET.get('created_on'))
    if request.GET and not contacts:
        messages.error(request, 'No Data Found')
    return render(request, 'contactus/contactus-list.html',{
        "head_title":"Contact Us Management",
        "contacts":get_pagination(request,contacts),
        "full_name":request.GET.get('full_name') if request.GET.get('full_name') else "",
        "email":request.GET.get('email') if request.GET.get('email') else "",
        "mobile_no":request.GET.get('mobile_no') if request.GET.get('mobile_no') else "",
        "message":request.GET.get('message') if request.GET.get('message') else "",
        "created_on":request.GET.get('created_on') if request.GET.get('created_on') else "",
        "user":request.GET.get('user') if request.GET.get('user') else "",
    })


@admins_only
@check_permissions('contact_us.view_contact_us')
def ViewContactUsDetails(request, id):
    contact = ContactUs.objects.get(id=id)
    replies = ContactUsReply.objects.filter(contact=contact)
    replies = get_pagination(request,replies)
    return render(request, 'contactus/view-contactus.html',{"head_title":"Contact Us Management","contact":contact,"replies":replies})


@admins_only
@check_permissions('contact_us.reply_contact_us')
def ContactUsReplyView(request):
    if request.method == 'POST':
        contact = ContactUs.objects.get(id=request.POST.get('id'))
        reply = ContactUsReply.objects.create(
            contact = contact,
            reply_message = request.POST.get('reply_message'),
            created_by = request.user
        )
        SendUserEmail(request,contact.user,'EmailTemplates/contactus-reply.html','Contact Us Revert',contact.user.email,"",reply.reply_message,'Contact Us Revert','')
        messages.success(request,"Reply sent successfully!")
        return redirect('contact_us:view_contact',id=contact.id)


@admins_only
@check_permissions('contact_us.delete_contact_us')
def DeleteContactUs(request, id):
    ContactUs.objects.get(id=id).delete()
    messages.success(request,"Contact Deleted Successfully!")
    return redirect('contact_us:contactus_list')
    