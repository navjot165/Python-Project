from .views import *
from .sitemaps import *
from django.contrib import admin
from django.urls import re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap


admin.autodiscover()

app_name = 'frontend'

sitemaps = {
 'pages': StaticSitemap,
}


urlpatterns = [
    re_path(r'^sitemap.xml/$', sitemap, {'sitemaps': sitemaps}),
    re_path(r'^about-us/$', AboutUsview, name='about_us'),
    re_path(r'^terms-and-conditions/$', TermsAndConditionsView, name='terms_view'),
    re_path(r'^privacy-policy/$', PrivacyPolicy, name='privacy_policy'),
    re_path(r'^$', index, name='index'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


