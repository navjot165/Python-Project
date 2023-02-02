import os
import pymysql
from pathlib import Path
import environ

env = environ.Env()
environ.Env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent

pymysql.install_as_MySQLdb()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '#1t6w)dhnvti_3zo%#pz==p*nb=7ouh5fj8mufo$##xo_rzok6'

SITE_ID = 1

DEBUG = True

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    # 'django_crontab',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework.authtoken',
    'django.contrib.sitemaps',
    'accounts',
    'frontend',
    'api',
    'rest_framework',
    # 'backup',
    'django.contrib.humanize',
    'fcm_django',
    'django_db_logger',
    'logger',
    'page',
    'users',
    'routes',
    'bookings',
    'contact_us',
    'cities',
    'buses',
    'charging_sites',
    'captains',
    'drf_yasg',
    'holidays',
    'reviews',
    'offers',
    'dispatcher',
    'subadmin'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

# Database
################ FOR MYSQL #######################
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'basigo',
        'USER': 'root',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '3306',
        'CONN_MAX_AGE': 600,
        'OPTIONS':{'charset': 'utf8mb4',"init_command":"SET foreign_key_checks = 0;"}
    }
}

AUTHENTICATION_BACKENDS = ['accounts.backend.EmailLoginBackend']

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# CRONJOBS = [

#     # Will run at every 10th minute
#     ('*/10 * * * *', 'routes.cron.cancel_rides_cronjob'),
    
#     # Will run at 00:00 daily
#     ('0 0 * * *', 'routes.cron.expire_promocodes'),
#     ('0 0 * * *', 'dispatcher.cron.dispatch_rides'),
    
# ]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_X_FORWARDED_HOST = True

USE_L10N = True

USE_TZ = False

AUTH_USER_MODEL = "accounts.User"

STATIC_URL = '/static/'
if not DEBUG:
    STATICFILES_DIRS = (
        os.path.join(BASE_DIR, "static", "admin"),
    )
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
else:
    STATICFILES_DIRS = (
        os.path.join(BASE_DIR, "static", "admin"),
        os.path.join(BASE_DIR, 'static'),
    )

MEDIA_URL = '/media/'
MEDIA_ROOT = (
    os.path.join(BASE_DIR, 'media')
)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
       'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

# SWAGGER_SETTINGS = {
#     "DOC_EXPANSION": "none",
#     "TAGS_SORTER": "alpha",
#     "OPERATIONS_SORTER": "alpha",
#     "SECURITY_DEFINITIONS": {
#         "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"}
#     },
# }

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'verbose': {
#             'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
#         },
#         'simple': {
#             'format': '%(levelname)s %(asctime)s %(message)s'
#         },
#     },
#     'handlers': {
#         'db_log': {
#             'level': 'DEBUG',
#             'class': 'django_db_logger.db_log_handler.DatabaseLogHandler'
#         },
#     },
#     'loggers': {
#         'db': {
#             'handlers': ['db_log'],
#             'level': 'DEBUG'
#         },
#         'django.request': {
#             'handlers': ['db_log'],
#             'level': 'ERROR',
#             'propagate': False,
#         }
#     }
# }


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True  

## Testing Creds
EMAIL_HOST = ''  
EMAIL_PORT = 587
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER