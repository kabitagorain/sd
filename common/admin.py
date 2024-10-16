from django.contrib import admin
from django.contrib.sites.models import Site
from common.models import SiteMeta
admin.site.unregister(Site)
admin.site.register(SiteMeta)
admin.site.register(Site)
