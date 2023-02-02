from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from pyfcm import FCMNotification
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
import pytz
import random
import environ
import logging
from bookings.models import *
from accounts.models import *
from logger.models import *
from accounts.constants import *
from datetime import datetime, date, timedelta
db_logger = logging.getLogger('db')
env = environ.Env()
environ.Env.read_env()


def SendUserEmail(request,user,template_name,mail_subject,to_email,token,description,title,password):
    use_https=False
    current_site = get_current_site(request)
    site_name = current_site.name
    context = {
        'domain':current_site.domain,
        'site_name': site_name,
        'protocol': 'https' if use_https else 'http',
        'user':user,
        'token':token if token else "",
        'description':description if description else "",
        'title':title if title else "",
        'password':password if password else "",
    }
    message = render_to_string(str(template_name), context)        
    email_message = EmailMultiAlternatives(mail_subject, message, settings.EMAIL_HOST_USER, [to_email])
    html_email = render_to_string(str(template_name),context)
    email_message.attach_alternative(html_email, 'text/html')
    status = email_message.send()
    EmailLogger.objects.create(
        reciever = user,
        email_template = html_email,
        recievers_email = to_email,
        sender_email = settings.EMAIL_HOST_USER,
        sent_status = True if status else False
    )


def SendNotification(created_by,created_for,title,description,notification_type,captain):
    if not created_for:
        created_for = User.objects.get(is_superuser=True, role_id=ADMIN)
    notification = Notification.objects.create(
        title = title,
        description = description,
        created_for = created_for,
        captain = captain if captain else None,
        notification_type = notification_type,
        created_by = created_by
    )
    try:
        push_service = FCMNotification(api_key=env('FCM_SERVER_KEY'))
        device = Device.objects.filter(user = created_for).last()
        push_service.notify_single_device(
            registration_id = device.device_token if device else "",
            message_title = title, 
            message_body = description,
            sound = "default",
            badge = 1,
            data_message = {
                "title":title,
                "description":description,
                "notification_id":notification.id,
                "notification_type":notification_type
            } 
        )
    except:
        device = None


def get_pagination(request,data):
	page = request.GET.get('page', 1)
	paginator = Paginator(data, PAGE_SIZE)
	try:
		data = paginator.page(page)
	except PageNotAnInteger:
		data = paginator.page(1)
	except EmptyPage:
		data = paginator.page(paginator.num_pages)
	except Exception as e:
		data = None 
	return data 


def ChangeToLocalTimezone(data,user_timezone):
    local_tz = pytz.timezone("UTC")
    UTC_tz = pytz.timezone(user_timezone)
    return str(UTC_tz.normalize(local_tz.localize(data).astimezone(UTC_tz))).split(".")[0]


def ConvertToUTC(data,user_timezone):
    local_tz = pytz.timezone(user_timezone)
    UTC_tz = pytz.timezone("UTC")
    return datetime.strptime(str(UTC_tz.normalize(local_tz.localize(data).astimezone(UTC_tz))).split("+")[0], "%Y-%m-%d %H:%M:%S")


def UserAuthenticate(mobile_no, country_code, password, role_id):
    user = User.objects.filter(mobile_no=mobile_no, country_code=country_code, role_id=role_id).order_by('created_on').last()
    if user.check_password(password):
        return user
    else:
        return None


def GenerateReferralCode():
    code_chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    code = ''
    for i in range(0, 10):
        slice_start = random.randint(0, len(code_chars) - 1)
        code += code_chars[slice_start: slice_start + 1]  
    return code


# def GenerateBookingId():
#     code_chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
#     code = ''
#     for i in range(0, 8):
#         slice_start = random.randint(0, len(code_chars) - 1)
#         code += code_chars[slice_start: slice_start + 1]  
#     return str('B-') + code


def GetWeekDates():
    today_date = date.today()
    weekday = today_date.isoweekday()
    start = today_date - timedelta(days=weekday)
    return [start + timedelta(days=d) for d in range(7)] 