from django.conf import settings
if ("rma_sent", "RMA Sent") not in settings.RMA_STATUS:
    raise ValueError('("rma_sent", "RMA Sent") must have in the settings.RMA_STATUS ')