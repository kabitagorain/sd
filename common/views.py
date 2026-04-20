from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from common.tasks import process_rma_email
import logging
from django.conf import settings
import requests
from django.core.cache import cache

log = logging.getLogger("log")


def get_immutable_id(volatile_message_id):
    # 1. Get an access token
    token_url = f"https://login.microsoftonline.com/{settings.M65_GRP_TENANT_ID}/oauth2/v2.0/token"
    token_data = {
        "grant_type": "client_credentials",
        "client_id": settings.M65_GRP_APP_ID,
        "client_secret": settings.M65_GRP_CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default",
    }
    access_token = requests.post(token_url, data=token_data).json().get("access_token")

    # 2. Make the API call to Graph to get the internetMessageId
    graph_url = f"https://graph.microsoft.com/v1.0/users/ehaines@edsystemsinc.com/messages/{volatile_message_id}?$select=internetMessageId"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(graph_url, headers=headers)

    if response.status_code == 200:
        return response.json().get("internetMessageId")
    return None


@csrf_exempt
def ms_graph_webhook(request):
    # STEP A: Microsoft Validation Handshake
    # Microsoft sends a POST request, but the token is in the query string (request.GET)
    validation_token = request.GET.get("validationToken")
    if validation_token:
        # Must return the token as plain text with a 200 status
        return HttpResponse(validation_token, content_type="text/plain", status=200)

    # STEP B: Process Actual Email Notification
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Notifications come in a 'value' array
            for notification in data.get("value", []):
                resource_data = notification.get("resourceData", {})
                message_id = resource_data.get("id")

                if message_id:
                    immutable_id = get_immutable_id(message_id)
                    if immutable_id is not None:
                        message_id = immutable_id
                        lock_key = f"rma_processed_immutable_{message_id}"
                        # If this message_id is already in the cache, skip it
                        if cache.get(lock_key):
                            print(
                                f"Skipping duplicate webhook for message {message_id}"
                            )
                            continue
                        # Mark it as processed
                        cache.set(lock_key, True, timeout=3600)
                        # Hand it off to Celery immediately
                        process_rma_email.delay(message_id)
        except Exception as e:
            log.error(f"Error processing Microsoft Graph webhook: {e} ")
            return HttpResponse(validation_token, status=200)  # Bad Request

        return HttpResponse(status=202)  # Tell MS we got it instantly
    return HttpResponse(validation_token, status=400)
