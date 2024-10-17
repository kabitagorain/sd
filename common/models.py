from django.db import models
from django.contrib.sites.models import Site


class SiteMeta(models.Model):
    """
    Represents metadata associated with a Site.

    This model extends the Site model by adding additional fields, such as
    title, description, keywords, logo, social media links, and a return address.

    Attributes:
        site (Site): The associated Site instance (one-to-one relationship).
        title (str): The title of the site (optional).
        description (str): A brief description of the site (optional).
        keywords (str): Keywords associated with the site (optional).
        logo (ImageField): The site logo (optional).
        social_logo (ImageField): The social media logo for the site (optional).
        return_address (str): The return address associated with the site.
        facebook (URLField): Facebook page URL for the site.
        x_twitter (URLField): Twitter page URL for the site.
        linkedin (URLField): LinkedIn profile URL for the site.
        instagram (URLField): Instagram profile URL for the site.
    """

    site = models.OneToOneField(
        Site, primary_key=True, on_delete=models.CASCADE, related_name="meta_data"
    )
    title = models.CharField(max_length=80, blank=True, null=True)
    description = models.TextField(max_length=200, null=True, blank=True)
    keywords = models.CharField(max_length=255, null=True, blank=True)
    logo = models.ImageField(upload_to="site_meta/")
    social_logo = models.ImageField(upload_to="site_meta/")
    return_address = models.TextField(
        default="E.D. Systems Tech Center\n"
        "3798 Oleander Ave #2\n"
        "Fort Pierce, Florida 34982\n"
        "United States."
    )
    facebook = models.URLField(default="#")
    x_twitter = models.URLField(default="#")
    linkedin = models.URLField(default="#")
    instagram = models.URLField(default="#")

    def __str__(self):
        """
        Returns a string representation of the SiteMeta instance.

        Returns:
            str: A string containing the site name and domain.
        """
        return f"Site Objects {self.site.name} - Domain {self.site.domain}"
