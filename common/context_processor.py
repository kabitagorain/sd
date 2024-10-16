from common.models import SiteMeta
from django.contrib.sites.models import Site
from django.core.cache import cache

def site_info(): 
    data = cache.get('site_data')

    if data is not None:
        return data

    site = Site.objects.get()

    try:  
        meta_data = site.meta_data
    except SiteMeta.DoesNotExist:      
        meta_data = SiteMeta(site=site)
        meta_data.save()

    data = {
        'name': meta_data.site.name,
        'title': meta_data.title,
        'domain': meta_data.site.domain,
        'description': meta_data.description,
        'keywords': meta_data.keywords, 
        'logo': meta_data.logo.url if meta_data.logo else '', 
        'og_image': meta_data.social_logo.url if meta_data.social_logo else '',
        'return_address' : meta_data.return_address,
        'facebook': meta_data.facebook,
        'x_twitter': meta_data.x_twitter,
        'linkedin': meta_data.linkedin,
        'instagram': meta_data.instagram,
    }

    cache.set('site_data', data, timeout=3600)

    return data

def sd_context(request):  
    site_data = site_info()
    context = {     
        'site_data': site_data,    
    }

    return context