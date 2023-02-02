import re
import json
from .models import *
from bookings.models import *
import random

def GetHeaders(request=None):
	regex = re.compile('^HTTP_')
	return dict((regex.sub('', header), value) for (header, value) in request.META.items() if header.startswith('HTTP_'))


def GetClientIP(request):
	try:
		x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
		if x_forwarded_for:
			ip = x_forwarded_for.split(',')[0]
		else:
			ip = request.META.get('REMOTE_ADDR')
		return ip
	except:
		return ''


"""
Hides sensitive keys specified in sensitive_keys settings.
Loops recursively over nested dictionaries.
"""
def MaskSensitiveData(data):
	if type(data) != dict:
		return data
	for key, value in data.items():
		if type(value) == dict:
			data[key] = MaskSensitiveData(data[key])
		if type(value) == list:
			data[key] = [MaskSensitiveData(item) for item in data[key]]
	return data


def CreateActionActivityLog(request, response_body, status_code, action_type):
    log = ActionActivityLogs.objects.create(
        api_url = request.build_absolute_uri(),
        headers = MaskSensitiveData(GetHeaders(request=request)),
        body_data = MaskSensitiveData(json.dumps(request.data) if request.data else ''),
        api_method = request.method,
        ip_address = GetClientIP(request),
        api_response = MaskSensitiveData(response_body),
        status_code = status_code,
        user = request.user if not request.user.is_anonymous else None,
        action_type = action_type
    )
    return log


def GenerateTransactionID():
    code_chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    code = ''
    for i in range(0, 10):
        slice_start = random.randint(0, len(code_chars) - 1)
        code += code_chars[slice_start: slice_start + 1]  
    return str('TR-') + code


def CreateTransaction(created_by, created_for, amount, booking, transaction_type,currency):
    transaction = Transactions.objects.create(
        transaction_id = GenerateTransactionID(),
        created_by = created_by,
        created_for = created_for,
        amount = round(float(amount if amount else 0),2),
        booking = booking,
        transaction_type = transaction_type,
        currency = currency
    )


def GenerateBoardingPass(ride):
    boarding_pass = random.randint(1, 100)
    if Booking.objects.filter(ride=ride,boarding_pass=boarding_pass):
        GenerateBoardingPass(ride)
    else:
        return boarding_pass