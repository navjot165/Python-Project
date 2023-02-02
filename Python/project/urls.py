from django.contrib import admin
from django.conf.urls import include, url
from frontend.views import *
from accounts.views import  *
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import  AdminLoginView
from django.views.static import serve

urlpatterns = [
    url(r'^admin/login/', AdminLoginView.as_view()),
    path('admin/', admin.site.urls),
    path('',include('frontend.urls')),
    path('api/', include('api.urls',)),
    path('accounts/', include('accounts.urls',)),
    path('accounts/', include('django.contrib.auth.urls')),
    # path('backup/', include('backup.urls',)),
    path('', include('cities.urls',)),
    path('logger/', include('logger.urls',)),
    path('static-pages/', include('page.urls',)),
    path('users/', include('users.urls',)),
    path('buses/', include('buses.urls',)),
    path('routes/', include('routes.urls',)),
    path('captains/', include('captains.urls',)),
    path('bookings/', include('bookings.urls',)),
    path('contact-us/', include('contact_us.urls')),
    path('charging-sites/', include('charging_sites.urls')),
    path('rating-reviews/', include('reviews.urls')),
    path('offers/', include('offers.urls')),
    path('dispatcher/', include('dispatcher.urls')),
    path('sub-admins/', include('subadmin.urls')),
    path('', include('holidays.urls')),
    url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}), 
    url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}), 
]

if settings.DEBUG is False:
    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

handler404 = 'frontend.views.handler404'
handler500 = 'frontend.views.handler500'
handler403 = 'frontend.views.handler403'
handler400 = 'frontend.views.handler400'