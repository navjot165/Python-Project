import json
from accounts.utils import *
from .serializer import *
from page.models import *
from accounts.models import *
from captains.models import *
from contact_us.models import *
from accounts.constants import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password
from django.contrib.auth import logout,login
from django.db.models import Q
from .utils import *


class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        if not request.data.get("mobile_no"):
            return Response({"message":"Please enter mobile number","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("country_code"):
            return Response({"message":"Please enter country code","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("password"):
            return Response({"message":"Please enter password"},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("role_id"):
            return Response({"message":"Please select role id","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            user = UserAuthenticate(
                mobile_no = request.data.get("mobile_no"), 
                country_code = request.data.get("country_code"), 
                password = request.data.get("password"),
                role_id = request.data.get("role_id"),
            )
        except:
            return Response({"message":"Invalid Login Credentials.", "status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not user:
            return Response({"message":"Invalid Login Credentials.", "status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if user.status == INACTIVE:
            return Response({"message":"Your account has been deactivated. Please contact admin to activate your account.","status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        elif user.status == DELETED:
            return Response({"message":"Your account has been deleted. Please contact admin.","status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        elif user.status == ACTIVE:
            if user.role_id == CAPTAIN:
                try:
                    captain = Captain.objects.get(user=user)
                except:
                    return Response({"message": "Captain matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST}) 
            else:
                captain = None 
            if not user.otp_verified:
                user.temp_otp = TEMP_OTP
                user.save()
                message = "An OTP has been sent on your mobile number. Please verify your account.Your OTP is "+str(TEMP_OTP)
            else:    
                if captain:
                    if not user.is_profile_verified:
                        return Response({"message": "Your account is under verification. Once it's verified you will able to login.","status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        message = "Login Successfully"
                else:
                    message = "Login Successfully"
            login(request, user)
            user.save()
            Token.objects.filter(user = user).delete()
            token = Token.objects.create(user = user)
            try:
                device = Device.objects.get(user = user)
            except Device.DoesNotExist:
                device = Device.objects.create(user = user)
            device.device_type = request.data['device_type']
            device.device_name = request.data['device_name']
            device.device_token = request.data['device_token']
            device.save()
            if captain:
                data = CaptainSerializer(captain,context = {"request":request}).data
            else:
                data = UserSerializer(user,context = {"request":request}).data
            data.update({"token":token.key})   
            return Response({"message":message,"data":data,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)


class SignupCustomerView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        if not request.data.get("first_name"):
            return Response({"message":"Please enter first name","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("mobile_no"):
            return Response({"message":"Please enter mobile number","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("country_code"):
            return Response({"message":"Please enter country code","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("email"):
            return Response({"message":"Please enter email","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("password"):
            return Response({"message":"Please enter password","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("role_id"):
            return Response({"message":"Please select role id","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("gender"):
            return Response({"message":"Please select gender","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(Q(status=ACTIVE)|Q(status=INACTIVE),email=request.data.get("email"), role_id=request.data.get("role_id")):
            return Response({"message":"There is already a registered user with this email id.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(Q(status=ACTIVE)|Q(status=INACTIVE),mobile_no=request.data.get("mobile_no"), role_id=request.data.get("role_id")):
            return Response({"message":"There is already a registered user with this mobile number.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        
        if request.data.get('referral_code'):
            referrer = User.objects.filter(referral_code=request.data.get('referral_code'),status=ACTIVE,role_id=request.data.get("role_id")).last()
            if not referrer:
                return Response({"message":"Invalid Referral Code"},status=status.HTTP_400_BAD_REQUEST)
        else:
            referrer = None
        user = User.objects.create(
            first_name = request.data.get("first_name"),
            last_name = request.data.get("last_name"),
            full_name = request.data.get("first_name") + " " + request.data.get("last_name") if request.data.get("last_name") else request.data.get("first_name"),
            email = request.data.get("email"),
            mobile_no = request.data.get("mobile_no"),
            country_code = request.data.get("country_code"),
            password = make_password(request.data.get("password")),
            role_id = request.data.get("role_id"),
            gender = request.data.get("gender"),
            temp_otp = TEMP_OTP,
            referral_code = GenerateReferralCode(),
            is_profile_verified = True,
        )
        try:
            UserWallet.objects.get(user=user)
        except:
            UserWallet.objects.create(user=user)
        Token.objects.filter(user = user).delete()
        token = Token.objects.create(user = user)      
        try:
            device = Device.objects.get(user = user)
        except Device.DoesNotExist:
            device = Device.objects.create(user = user)
        device.device_type = request.data['device_type']
        device.device_name = request.data['device_name']
        device.device_token = request.data['device_token']
        device.save()
        if referrer:
            user.is_referred = True
            user.referred_by = referrer
            user.save()
            UserReferralCodeUsed.objects.create(referrer=referrer,referee = user)
        data = UserSerializer(user,context = {"request":request}).data
        data.update({"token":token.key}) 
        return Response({"message":"User Registered Successfully! An OTP has been sent on your mobile number. Please verify your account. Your OTP is "+str(TEMP_OTP),"data":data},status=status.HTTP_200_OK)


class SignupCaptainView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        if not request.data.get("first_name"):
            return Response({"message":"Please enter first name","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("mobile_no"):
            return Response({"message":"Please enter mobile number","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("country_code"):
            return Response({"message":"Please enter country code","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("email"):
            return Response({"message":"Please enter email","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("password"):
            return Response({"message":"Please enter password","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("role_id"):
            return Response({"message":"Please select role id","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("gender"):
            return Response({"message":"Please select gender","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("years_of_experience"):
            return Response({"message":"Please enter years of experience","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("driving_license_expiry_date"):
            return Response({"message":"Please select driving license expiry date","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(Q(status=ACTIVE)|Q(status=INACTIVE),email=request.data.get("email"), role_id=request.data.get("role_id")):
            return Response({"message":"There is already a registered user with this email id.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(Q(status=ACTIVE)|Q(status=INACTIVE),mobile_no=request.data.get("mobile_no"), role_id=request.data.get("role_id")):
            return Response({"message":"There is already a registered user with this mobile number.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        
        if request.data.get('referral_code'):
            referrer = User.objects.filter(referral_code=request.data.get('referral_code'),status=ACTIVE,role_id=request.data.get("role_id")).last()
            if not referrer:
                return Response({"message":"Invalid Referral Code"},status=status.HTTP_400_BAD_REQUEST)
        else:
            referrer = None
        user = User.objects.create(
            first_name = request.data.get("first_name"),
            last_name = request.data.get("last_name"),
            full_name = request.data.get("first_name") + " " + request.data.get("last_name") if request.data.get("last_name") else request.data.get("first_name"),
            email = request.data.get("email"),
            mobile_no = request.data.get("mobile_no"),
            country_code = request.data.get("country_code"),
            password = make_password(request.data.get("password")),
            role_id = request.data.get("role_id"),
            gender = request.data.get("gender"),
            temp_otp = TEMP_OTP,
            referral_code = GenerateReferralCode()
        )
        if referrer:
            user.is_referred = True
            user.referred_by = referrer
            user.save()
            UserReferralCodeUsed.objects.create(referrer=referrer,referee = user)
        captain = Captain.objects.create(
            user = user,
            years_of_experience = request.data.get("years_of_experience"),
            driving_license_expiry_date = request.data.get("driving_license_expiry_date")
        )
        try:
            UserWallet.objects.get(user=user)
        except:
            UserWallet.objects.create(user=user)
        for i in range(0,int(request.data.get("govt_id_proof_count",'0'))+1):
            if request.FILES.get("govt_id_proof_image{}".format(i),None):
                captain.govt_id_proof.add(Image.objects.create(upload=request.FILES.get("govt_id_proof_image{}".format(i)),user = user))
        for i in range(0,int(request.data.get("driving_license_count",'0'))+1):
            if request.FILES.get("driving_license_image{}".format(i),None):
                captain.driving_license.add(Image.objects.create(upload=request.FILES.get("driving_license_image{}".format(i)),user = user))
        Token.objects.filter(user = user).delete()
        token = Token.objects.create(user = user)      
        try:
            device = Device.objects.get(user = user)
        except Device.DoesNotExist:
            device = Device.objects.create(user = user)
        device.device_type = request.data['device_type']
        device.device_name = request.data['device_name']
        device.device_token = request.data['device_token']
        device.save()
        SendNotification(user,None,"Pending Captain Verification","Captain profile verification is pending.",CAPTAIN_VERIFICATION_NOTIFICATION,captain)
        data = CaptainSerializer(captain,context = {"request":request}).data
        data.update({"token":token.key}) 
        return Response({"message":"User Registered Successfully! An OTP has been sent on your mobile number. Please verify your account. Your OTP is "+str(TEMP_OTP),"data":data},status=status.HTTP_200_OK)


class ResendOTP(APIView):
    permission_classes = (permissions.IsAuthenticated,) 

    def get(self, request):
        user = User.objects.get(id=request.user.id)
        if user.otp_verified:
            return Response({"message":"User account has already been verified"},status=status.HTTP_400_BAD_REQUEST)
        else:
            user.temp_otp = TEMP_OTP
            user.save()
            return Response({"message":"An OTP has been sent on your mobile number. Please verify your account. Your OTP is "+str(TEMP_OTP)},status=status.HTTP_200_OK)


class VerifyOTP(APIView):
    permission_classes = (permissions.IsAuthenticated,) 

    def get(self, request):
        if not request.query_params.get("otp"):
            return Response({"message":"Please enter otp","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(id=request.user.id)
        if user.role_id == CAPTAIN:
            try:
                captain = Captain.objects.get(user=user)
            except:
                return Response({"message": "Captain matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST}) 
        else:
            captain = None
        if user.temp_otp == request.query_params.get('otp'):
            login(request, user)
            Token.objects.filter(user = user).delete()
            token = Token.objects.create(user = user)
            user.temp_otp = ''
            user.otp_verified = True
            user.save()
            if captain:  
                data = CaptainSerializer(captain,context = {"request":request}).data
            else:
                data = UserSerializer(user,context = {"request":request}).data
            data.update({"token":token.key}) 
            return Response({"message":"OTP Verified Successfully.".format(user.temp_otp),"data":data},status=status.HTTP_200_OK)
        else:
            return Response({"message":"Incorrect OTP"},status=status.HTTP_400_BAD_REQUEST)


class EditProfileCustomer(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        if not request.data.get("first_name"):
            return Response({"message":"Please enter first name","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("email"):
            return Response({"message":"Please enter email","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("gender"):
            return Response({"message":"Please select gender","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=request.user.id)
        except:
            return Response({"message":"User matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(Q(status=ACTIVE)|Q(status=INACTIVE),email=request.data.get("email"), role_id=user.role_id).exclude(id=user.id):
            return Response({"message":"There is already a registered user with this email id.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        user.first_name = request.data.get("first_name")
        user.last_name = request.data.get("last_name")
        user.full_name = request.data.get("first_name") + " " + request.data.get("last_name") if request.data.get("last_name") else request.data.get("first_name")
        user.email = request.data.get("email")
        user.gender = request.data.get("gender")
        if request.FILES.get('profile_pic'):
            user.profile_pic = request.FILES.get('profile_pic')
        user.save()
        data = UserSerializer(user,context = {"request":request}).data
        return Response({"message":"Profile updated successfully!","data":data},status=status.HTTP_200_OK) 


class UpdateUserCity(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            city = Cities.objects.get(id=request.data.get('city'))
        except:
            return Response({"message":"City Matching query does not exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=request.user.id)
        except:
            return Response({"message":"User matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        user.city = city
        user.save()
        data = UserSerializer(user,context = {"request":request}).data
        return Response({"message":"City updated successfully!","data":data},status=status.HTTP_200_OK) 


class EditProfileCaptain(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        if not request.data.get("first_name"):
            return Response({"message":"Please enter first name","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("email"):
            return Response({"message":"Please enter email","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("gender"):
            return Response({"message":"Please select gender","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("years_of_experience"):
            return Response({"message":"Please enter years of experience","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("driving_license_expiry_date"):
            return Response({"message":"Please select driving license expiry date","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=request.user.id)
        except:
            return Response({"message":"User matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            captain = Captain.objects.get(user=user)
        except:
            return Response({"message": "Captain matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST}) 
        
        if User.objects.filter(Q(status=ACTIVE)|Q(status=INACTIVE),email=request.data.get("email"), role_id=user.role_id).exclude(id=user.id):
            return Response({"message":"There is already a registered user with this email id.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        user.first_name = request.data.get("first_name")
        user.last_name = request.data.get("last_name")
        user.full_name = request.data.get("first_name") + " " + request.data.get("last_name") if request.data.get("last_name") else request.data.get("first_name")
        user.email = request.data.get("email")
        user.gender = request.data.get("gender")
        captain.years_of_experience = request.data.get("years_of_experience")
        captain.driving_license_expiry_date = request.data.get("driving_license_expiry_date")
        if request.FILES.get('profile_pic'):
            user.profile_pic = request.FILES.get('profile_pic')
        for i in range(0,int(request.data.get("govt_id_proof_count",'0'))+1):
            if request.FILES.get("govt_id_proof_image{}".format(i),None):
                captain.govt_id_proof.add(Image.objects.create(upload=request.FILES.get("govt_id_proof_image{}".format(i)),user = user))
        for i in range(0,int(request.data.get("driving_license_count",'0'))+1):
            if request.FILES.get("driving_license_image{}".format(i),None):
                captain.driving_license.add(Image.objects.create(upload=request.FILES.get("driving_license_image{}".format(i)),user = user))
        user.save()
        captain.save()
        data = CaptainSerializer(captain,context = {"request":request}).data
        return Response({"message":"Profile updated successfully!","data":data},status=status.HTTP_200_OK) 
        

class LogoutView(APIView): 
    permission_classes = (permissions.IsAuthenticated,) 

    def get(self, request):
        try:
            user = User.objects.get(id=request.user.id)
        except:
            return Response({"message": "User matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)  
        Token.objects.filter(user=user).delete()
        logout(request)       
        return Response({"message":"Logout Successfully!","status":status.HTTP_200_OK}, status=status.HTTP_200_OK)


class UserCheckView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        try:
            user = User.objects.get(id=request.user.id)
        except:
            return Response({"message": "User matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST})  
        try:
            token = Token.objects.get(user = request.user)
        except:
            token = Token.objects.create(user = request.user)
        if user.role_id == CAPTAIN:
            try:
                captain = Captain.objects.get(user=user)
            except:
                return Response({"message": "Captain matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST})  
            data = CaptainSerializer(captain,context = {"request":request}).data
        else:
            data = UserSerializer(user,context = {"request":request}).data
        data.update({"token":token.key})  
        if user.is_profile_verified:
            return Response({"data":data,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)
        else:
            return Response({"data":data,"status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)


class GetProfileDetails(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        try:
            user = User.objects.get(id=request.user.id)
        except:
            return Response({"message": "User matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST}) 
        if user.role_id == CAPTAIN:
            try:
                captain = Captain.objects.get(user=user)
            except:
                return Response({"message": "Captain matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST})  
            data = CaptainSerializer(captain,context = {"request":request}).data
        else:
            data = UserSerializer(user,context = {"request":request}).data
        return Response({"data":data,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)


class ForgetPassword(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        if not request.data.get("email"):
            return Response({"message":"Please enter email","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("role_id"):
            return Response({"message":"Please select role id","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not User.objects.filter(email = request.data.get("email"),status=ACTIVE, role_id=request.data.get("role_id")):
            return Response({"message": "Please enter a registered email id","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)  
        else:
            try:
                user = User.objects.get(email= request.data.get("email"),status=ACTIVE, role_id=request.data.get("role_id")) 
            except:
                return Response({"message": "User matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 
            try:
                token = Token.objects.get(user=user)
            except:
                token = Token.objects.create(user=user)  
            SendUserEmail(request,user,'EmailTemplates/ResetPassword.html','Reset Password',request.data.get("email"),token,"","","")
            return Response({"message": "A link has been sent on your email to reset your password.","status":status.HTTP_200_OK}, status=status.HTTP_200_OK)


class ChangePassword(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=request.user.id) 
        except:
            return Response({"message": "User matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 
        
        if not request.data.get("password"):
            return Response({"message":"Please enter password","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        
        user.password = make_password(request.data.get("password"))
        user.save()
        Token.objects.filter(user=user).delete()
        logout(request)       
        return Response({"message":"Password updated successfully!","status":status.HTTP_200_OK}, status=status.HTTP_200_OK)


class StaticPages(APIView):

    def get(self, request, *args, **kwargs):
        if not request.query_params.get('page_id'):
            return Response({"message": "Please enter page id.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 
        try:
            page = Pages.objects.get(type_id=request.query_params.get('page_id'))
            data = PagesSerializer(page,context = {"request":request}).data
            CreateActionActivityLog(request, json.dumps(data), status.HTTP_200_OK, API_ACTION)
            return Response({"data":data,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)
        except:
            CreateActionActivityLog(request, "No data found.", status.HTTP_200_OK, API_ACTION)
            return Response({"message":"No data found.","status":status.HTTP_200_OK}, status=status.HTTP_200_OK)


class DeleteAccount(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        try:
            user = User.objects.get(id=request.user.id)
        except:
            return Response({"message": "User matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)  
        user.status = DELETED
        user.save()
        Token.objects.filter(user=user).delete()
        Device.objects.filter(user=user).delete()
        logout(request) 
        return Response({"message":"Account Deleted Successfully!","status":status.HTTP_200_OK}, status=status.HTTP_200_OK)


class DeleteDocuments(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        try:
            image = Image.objects.get(id=request.query_params.get('document_id'))
        except:
            return Response({"message": "Document matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 
        image.delete()
        if request.user.role_id == CAPTAIN:
            try:
                captain = Captain.objects.get(user=request.user)
            except:
                return Response({"message": "Captain matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST})  
            data = CaptainSerializer(captain,context = {"request":request}).data
        else:
            data = UserSerializer(request.user,context = {"request":request}).data
        return Response({"message":"Document Deleted Successfully!","data":data,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)


class ContactUsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        if not request.data.get('full_name'):
            return Response({"message": "Please enter the full name","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('email'):
            return Response({"message": "Please enter the email","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('mobile_no'):
            return Response({"message": "Please enter the mobile number","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('message'):
            return Response({"message": "Please enter the message","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)

        try:
            contact_us = ContactUs.objects.get(
                full_name = request.data.get('full_name'),
                email = request.data.get('email'),
                mobile_no = request.data.get('mobile_no'),
                message = request.data.get('message'),
                user = request.user
            )
            data = ContactUsSerializer(contact_us,context={"request":request}).data
            return Response({"message":"You have already raised the same query before!","data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK) 
        except:
            contact_us = ContactUs.objects.create(
                full_name = request.data.get('full_name'),
                email = request.data.get('email'),
                mobile_no = request.data.get('mobile_no'),
                message = request.data.get('message'),
                user = request.user
            )
            data = ContactUsSerializer(contact_us,context={"request":request}).data
            return Response({"message":"Thank you for contacting us. We will get back to you shortly!","data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK) 


class CitiesList(APIView):
    permission_classes = (permissions.AllowAny, )

    def get(self, request, *args, **kwargs):
        cities = Cities.objects.all().order_by('name')
        if request.query_params.get('search'):
            cities = cities.filter(name__icontains = request.query_params.get('search'))
        data = CitiesSerializer(cities,many=True,context={"request":request}).data
        return Response({"data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)