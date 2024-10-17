"""
Admin Site Configuration

This section configures the appearance and display of the Django admin site.

Attributes:
    admin.site.site_header (str): Header displayed on the admin login page.
    admin.site.site_title (str): Title displayed on the admin pages.
    admin.site.index_title (str): Title displayed on the admin index page.
    admin.empty_value_display (str): Placeholder text for empty fields.

URL Configuration

This module defines the URL routes for the Django project. It includes URLs 
for the admin site and several applications, such as `common`, `account`, and `rma`.

URL Patterns:
    - 'admin/': Admin site URLs.
    - '': Common application URLs (root).
    - 'account/': Account management URLs.
    - 'rma/': RMA (Return Merchandise Authorization) URLs.

If `DEBUG` is enabled, static and media files are served during development.

Attributes:
    urlpatterns (list): List of URL patterns to be used by the project.

Raises:
    ImproperlyConfigured: If URLs are incorrectly set up or missing.
"""


from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

# Configure the Django admin site headers and display values
admin.site.site_header = 'ED System admin'
admin.site.site_title = 'ED System admin'
admin.site.index_title = 'ED System administration'
admin.empty_value_display = '**Empty**'

# Define URL patterns for the project
urlpatterns = [
    path('admin/', admin.site.urls), 
    path('', include('common.urls')),   
    path('account/', include('account.urls')),
    path('rma/', include('rma.urls')),            
]

if settings.DEBUG:
    # Serve media and static files during development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
