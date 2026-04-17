# views.py
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

from common.tasks import process_rma_email  # We'll create this next


@csrf_exempt
def ms_graph_webhook(request):
    # STEP A: Microsoft Validation Handshake (GET)
    if request.method == "GET":
        validation_token = request.GET.get("validationToken")
        if validation_token:
            # MUST return the actual variable, not a string literal!
            return HttpResponse(validation_token, content_type="text/plain", status=200)
        return HttpResponse(validation_token, status=400)

    # STEP B: Process Notification (POST)
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
