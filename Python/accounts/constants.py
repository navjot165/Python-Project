TEMP_OTP = 1234

"""
User role type name
"""
USER_ROLE = ((1, "Admin"),(2, "Customer"),(3,"Captain"),(4,"SubAdmin"))
ADMIN = 1
CUSTOMER = 2
CAPTAIN = 3
SUBADMIN = 4


"""
User Status 
"""
USER_STATUS = ((1, "Active"),(2,"Inactive"),(3,"Deleted"),(4, "Suspended"),(5,"Terminated"))
ACTIVE = 1
INACTIVE = 2
DELETED = 3
SUSPENDED = 4
TERMINATED = 5


"""
Device
"""
DEVICE_TYPE  = ((1,"Android"),(2,"IOS"))
ANDROID = 1
IOS = 2


"""
Social Logins
"""
SOCIAL_TYPE = ((1,'Google'),(2,'Instagram'),(3,'Facebook'),(4,'Apple'))
GOOGLE = 1
INSTAGRAM = 2
FACEBOOK = 3
APPLE = 4


"""
Page Type
"""
PAGE_TYPE =  ((1,"Terms_And_Condition"),(2,"Privacy_Policy"),(3, "About_Us"),(4, "Ride Cancellation Policy"))
TERMS_AND_CONDITION = 1
PRIVACY_POLICY = 2
ABOUT_US = 3
RIDE_CANCELLATION_POLICY = 4


"""
PAGE SIZE
"""
PAGE_SIZE = 15
API_PAGINATION = 10


"""
Ride Status
"""
RIDE_STATUS  = ((1,"SCHEDULED"),(2, "INPROGRESS"),(3,"CANCELLED"),(4,"COMPLETED"),(5,"ARRIVED_AT_STATION"),(6,"STOPPED_RIDE"))
SCHEDULED_RIDE = 1
INPROGRESS_RIDE = 2
CANCELLED_RIDE = 3
COMPLETED_RIDE = 4
ARRIVED_AT_STATION = 5
STOPPED_RIDE = 6


"""
Cancellation Reasons
"""
CANCELLATION_REASONS = ((1,'CANCEL_BOOKING_REASON'),)
CANCEL_BOOKING_REASON = 1


"""
Booking Status
"""
BOOKING_STATUS = ((1,"BOOKED"),(2,"COMPLETE"),(3,"CANCELLED"),(4,"MISSED"))
BOOKED = 1
COMPLETE_BOOKING = 2
CANCELLED_BOOKING = 3
MISSED_BOOKING = 4


"""
Notification Type
"""
NOTIFICATION_TYPE = ((1, 'Booking'), (2, 'Schedule'), (3, 'Rating'))
CAPTAIN_VERIFICATION_NOTIFICATION = 1
BOOKING_NOTIFICATION = 2



"""
Transaction Type
"""
TRANSACTION_TYPE = ((1, 'Amount_Recieved'),(2,'Amount_Deducted'))
AMOUNT_RECIEVED = 1
AMOUNT_DEDUCTED = 2


"""
GENDER
"""
GENDER = ((1,'Male'), (2, 'FEMALE'), (3,'Other'))
MALE = 1
FEMALE = 2
OTHER = 3


"""
Address Types
"""
ADDRESS_TYPE = ((1,'Home'),(2,'Office'),(3,'Other'))
HOME_ADDRESS = 1
OFFICE_ADDRESS = 2
OTHER_ADDRESS = 3


"""
City State
"""
CITY_STATE = ((1,'Active'), (2, 'Inactive'))
ACTIVE_CITY = 1
INACTIVE_CITY = 1


"""
User Category
"""
USER_CATEGORY = ((1,'HV'),(2,'MV'),(3,'LV'))
HV = 1 
MV = 1 
LV = 1 


"""
Dispatch Types
"""
DISPATCH_TYPES = ((1,'Automatic'), (2,'Manual'))
AUTOMATIC = 1
MANUAL = 2


"""
Ride Category
"""
RIDE_CATEGORY = ((1,'EV'),(2,'NON_EV'),(3,'Premium'),(4,'Economy'))
EV = 1
NON_EV = 2
PREMIUM = 3
ECONOMY = 4


CATEGORY_FLAGS = ((1,'Premium'),(2,'Economy'))
CATEGORY_FLAG_PREMIUM = 1
CATEGORY_FLAG_ECONOMY = 2


CATEGORY_TYPE = ((1,'EV'),(2,'NON_EV'))
CATEGORY_TYPE_EV = 1
CATEGORY_TYPE_NON_EV = 2


PRICE_CONFIG_TYPE = ((1, 'Custom'), (2,'Category'))
CUSTOM_PRICE = 1
CATEGORY_PRICE = 2


PROMO_TYPE = ((1, 'Percentage'), (2,'Absolute'))
PERCENTAGE_PROMO = 1
ABSOLUTE_PROMO = 2


OFFER_TYPES = ((1,'Promo code'),(2,'Referral Rewards'))
OFFER_PROMO_TYPE = 1
OFFER_REFERRAL_REWARD_TYPE = 2


PROMO_STATUS = ((1,'Active'), (2,'Inactive'), (3,'Expired'))
ACTIVE_PROMO = 1
INACTIVE_PROMO = 2
EXPIRED_PROMO = 3


REFUND_TYPE = ((1,'Full_Refund'),(2,'Partial_Refund'))
FULL_REFUND = 1
PARTIAL_REFUND = 2


WALKING_DISTANCE_MODE = ((1,'Walking'), (2,'Driving'))
WALKING_MODE = 1
DRIVING_MODE = 2


COMPANY_TYPE = ((1,'Individual'),(2,'Sacco'))
INDIVIDUAL = 1
SACCO = 2


PAYMENT_MODE = ((1,'SACCO'),(2,'Individual'),(3,'Supplier'))
SACCO_MODE = 1
INDIVIDUAL_MODE = 2
SUPPLIER_MODE = 3


PLAN_TYPE = ((1,'Weekdays'),(2,'Weekend'),(3,'Both Weekdays & Weekend'))
WEEKDAYS_PLAN = 1
WEEKEND_PLAN = 2
BOTH_WEEKDAY_AND_WEEKEND = 3


SHIFT_TYPE = ((1,'FullTime'),(2,'PartTime'))
FULL_TIME = 1
PART_TIME = 2


ACTION_TYPES = ((1,'API_Action'),(2,'Backend_Action'))
API_ACTION = 1
BACKEND_ACTION = 2


BOOKING_PAYMENT_METHOD = ((1, 'MPesa'),(2,'Wallet'))
MPESA_PAYMENT_METHOD = 1
WALLET_PAYMENT_METHOD = 2


COMPANY_PAYMENT_MODE = ((1,'Bank Transfer'),(2,'Mobile Money'))
BANK_TRANSFER = 1
MOBILE_MONEY = 2


DISPATCHER_STATUS = ((1,'Dispatch Success'),(2,'Dispatch Failure'))
DISPATCH_SUCCESS = 1
DISPATCH_FAILED = 2