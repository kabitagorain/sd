from django.urls import path

from rma.views import rma_request_view
from .views import *

app_name = "common"

urlpatterns = [
    path("", rma_request_view, name="rma_request"),
]

"""
URL configuration for the 'common' app.

Currently, the 'common' app does not have specific routes, so it directs 
to the RMA request view as a placeholder.

Attributes:
    app_name (str): Namespace for the app, used in URL resolution.
    urlpatterns (list): List of URL patterns for the app.
"""
