"""
Ensures that the RMA status includes "rma_sent" in the settings configuration.

This function checks whether the tuple ("rma_sent", "RMA Sent") is present in the 
`settings.RMA_STATUS` configuration. The "rma_sent" status is mandatory for sending 
emails from the admin interface when reviewing the RMA (Return Merchandise Authorization). 
Changing the status to "rma_sent" allows sending instruction emails to the customer, 
thereby ensuring that the RMA process is correctly configured.

Raises:
    ValueError: If the tuple ("rma_sent", "RMA Sent") is not found in `settings.RMA_STATUS`.
"""

from django.conf import settings
if ("rma_sent", "RMA Sent") not in settings.RMA_STATUS:
    raise ValueError('("rma_sent", "RMA Sent") must have in the settings.RMA_STATUS ')
