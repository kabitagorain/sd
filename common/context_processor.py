from common.models import SiteMeta
from django.contrib.sites.models import Site
from django.core.cache import cache


def site_info():
    """
    Retrieves site metadata, either from cache or from the database.

    If cached data is available, it is returned immediately. Otherwise,
    the data is fetched from the database, and if no metadata exists for
    the site, a default SiteMeta instance is created. The fetched data
    is then cached for future use.

    Returns:
        dict: A dictionary containing site metadata, such as name, title,
        domain, description, keywords, logo, social media links, and
        return address.
    """

    data = cache.get("site_data")

    if data is not None:
        return data

    site = Site.objects.get()

    try:
        meta_data = site.meta_data
    except SiteMeta.DoesNotExist:
        meta_data = SiteMeta(site=site)
        meta_data.save()

    data = {
        "name": meta_data.site.name,
        "title": meta_data.title,
        "domain": meta_data.site.domain,
        "description": meta_data.description,
        "keywords": meta_data.keywords,
        "logo": meta_data.logo.url if meta_data.logo else "",
        "og_image": meta_data.social_logo.url if meta_data.social_logo else "",
        "return_address": meta_data.return_address,
        "facebook": meta_data.facebook,
        "x_twitter": meta_data.x_twitter,
        "linkedin": meta_data.linkedin,
        "instagram": meta_data.instagram,
    }

    cache.set("site_data", data, timeout=3600)

    return data


def sd_context(request):
    """
    Provides site metadata to be used in the template context.

    Args:
        request (HttpRequest): The current request object.

    Returns:
        dict: A dictionary containing site metadata under the key 'site_data'.
    """
    site_data = site_info()
    context = {
        "site_data": site_data,
    }

    return context
