from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticSitemap(Sitemap):
    changefreq = 'daily'
    priority = '0.5'

    def items(self):
        return [
            'accounts:login',
            'frontend:about_us',
            'frontend:terms_view',
            'frontend:privacy_policy',
        ]
    def location(self, item):
        return reverse(item)