from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from common.tasks import process_rma_email
import logging

from django.core.cache import cache

log = logging.getLogger("log")


@csrf_exempt
def ms_graph_webhook(request):
    # STEP A: Microsoft Validation Handshake (GET)
    validation_token = request.GET.get("validationToken")
    if validation_token:
        return HttpResponse(validation_token, content_type="text/plain", status=200)

    # STEP B: Process Actual Email Notification (POST)
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            for notification in data.get("value", []):
                resource_data = notification.get("resourceData", {})
                volatile_id = resource_data.get("id")

                if volatile_id:
                    # ATOMIC LOCK: Try to add this volatile ID to cache.
                    # If it returns False, we are already processing this specific ping.
                    lock_key = f"msg_ping_lock_{volatile_id}"
                    if cache.add(lock_key, True, timeout=300):
                        process_rma_email.delay(volatile_id)

            # ALWAYS return 202/200 immediately so Microsoft doesn't retry
            return HttpResponse(status=202)

        except Exception as e:
            log.error(f"Error in webhook view: {e}")
            return HttpResponse(status=200)  # Still return 200 to stop retries

    return HttpResponse(validation_token, status=400)


# @csrf_exempt
# def ms_graph_webhook(request):
#     # STEP A: Microsoft Validation Handshake
#     # Microsoft sends a POST request, but the token is in the query string (request.GET)
#     validation_token = request.GET.get("validationToken")
#     if validation_token:
#         # Must return the token as plain text with a 200 status
#         return HttpResponse(validation_token, content_type="text/plain", status=200)

#     # STEP B: Process Actual Email Notification
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)

#             # Notifications come in a 'value' array
#             for notification in data.get("value", []):
#                 resource_data = notification.get("resourceData", {})
#                 message_id = resource_data.get("id")

#                 if message_id:
#                     immutable_id = get_immutable_id(message_id)
#                     if immutable_id is not None:
#                         message_id = immutable_id
#                         lock_key = f"rma_processed_immutable_{message_id}"
#                         # If this message_id is already in the cache, skip it
#                         if cache.get(lock_key):
#                             print(
#                                 f"Skipping duplicate webhook for message {message_id}"
#                             )
#                             continue
#                         # Mark it as processed
#                         cache.set(lock_key, True, timeout=3600)
#                         # Hand it off to Celery immediately
#                         process_rma_email.delay(message_id)
#         except Exception as e:
#             log.error(f"Error processing Microsoft Graph webhook: {e} ")
#             return HttpResponse(validation_token, status=200)  # Bad Request

#         return HttpResponse(status=202)  # Tell MS we got it instantly
#     return HttpResponse(validation_token, status=400)
