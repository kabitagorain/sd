from django.urls import path

from rma.views import rma_request_view
from .views import *
app_name = 'common'

urlpatterns = [
    path('', rma_request_view, name='rma_request'),  
   
]
