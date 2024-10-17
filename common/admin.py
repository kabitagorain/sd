from django.contrib import admin
from django.contrib.sites.models import Site
from common.models import SiteMeta

admin.site.unregister(Site)
admin.site.register(SiteMeta)
admin.site.register(Site)


"""
Registers and manages the Site and SiteMeta models with the Django admin interface.

The Site model is first unregistered and then re-registered to allow for 
customized admin behavior. The SiteMeta model is also registered to manage 
site metadata through the admin site.
"""
