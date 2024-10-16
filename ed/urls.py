from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings


admin.site.site_header = 'ED System admin'
admin.site.site_title = 'ED System admin'
admin.site.index_title = 'ED System administration'
admin.empty_value_display = '**Empty**'


urlpatterns = [
    path('admin/', admin.site.urls), 
    path('', include('common.urls')),   
    path('account/', include('account.urls')),
    path('rma/', include('rma.urls')),            
        
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    
