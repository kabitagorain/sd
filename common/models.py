from django.db import models
from django.contrib.sites.models import Site

class SiteMeta(models.Model):
    site = models.OneToOneField(Site, primary_key=True, on_delete=models.CASCADE, related_name='meta_data')
    title = models.CharField(max_length=80, blank=True, null=True)
    description = models.TextField(max_length=200, null=True, blank=True)
    keywords = models.CharField(max_length=255, null=True, blank=True)
    logo = models.ImageField(upload_to='site_meta/')
    social_logo = models.ImageField(upload_to='site_meta/')
    return_address = models.TextField(
        default=
            'E.D. Systems Tech Center\n'
            '3798 Oleander Ave #2\n'
            'Fort Pierce, Florida 34982\n'
            'United States.'
        )
    facebook = models.URLField(default='#')
    x_twitter = models.URLField(default='#')
    linkedin = models.URLField(default='#')
    instagram = models.URLField(default='#')
    
    def __str__(self):
        return f"Site Objects {self.site.name} - Domain {self.site.domain}"

    