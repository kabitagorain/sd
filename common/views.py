from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from common.tasks import process_rma_email


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
                    # Hand it off to Celery immediately
                    process_rma_email.delay(message_id)
        except json.JSONDecodeError:
            pass

        return HttpResponse(status=202)  # Tell MS we got it instantly
