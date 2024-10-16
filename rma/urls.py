from django.urls import path
from .views import *
app_name = 'rma'

urlpatterns = [

   path('request/', rma_request_view, name='rma_request'),
   
   
]
