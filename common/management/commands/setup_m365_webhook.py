# ed /common/management/commands/setup_m365_webhook.py

import requests
import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone


class Command(BaseCommand):
    help = "Registers the Microsoft Graph Webhook"

    def handle(self, *args, **options):
        # 1. YOUR CREDENTIALS
        TENANT_ID = settings.M65_GRP_TENANT_ID
        CLIENT_ID = settings.M65_GRP_APP_ID
        CLIENT_SECRET = settings.M65_GRP_CLIENT_SECRET

        # The URL you set up in your Django urls.py
        NOTIFICATION_URL = "https://return.edsystemsinc.com/webhooks/msgraph/"
        USER_EMAIL = "ehaines@edsystemsinc.com"

        # 2. GET ACCESS TOKEN
        token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
        token_data = {
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope": "https://graph.microsoft.com/.default",
        }
        token_res = requests.post(token_url, data=token_data).json()
        access_token = token_res.get("access_token")

        if not access_token:
            self.stdout.write(self.style.ERROR(f"Auth Failed: {token_res}"))
            return

        # 1. Clean Expiry (Exactly what MS expects)
        # Use 4230 minutes max. Let's use 4000 to be safe.
        expiry_date = timezone.now() + datetime.timedelta(minutes=4000)
        expiry = expiry_date.strftime("%Y-%m-%dT%H:%M:%SZ")

        # 3. REGISTER WEBHOOK
        sub_url = "https://graph.microsoft.com/v1.0/subscriptions"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        sub_body = {
            "changeType": "created",
            "notificationUrl": NOTIFICATION_URL,
            "resource": "users/ehaines@edsystemsinc.com/messages",
            "expirationDateTime": expiry,
            "clientState": "SecretToken123",
        }

        response = requests.post(sub_url, headers=headers, json=sub_body)

        if response.status_code == 201:
            self.stdout.write(
                self.style.SUCCESS(f"Success! ID: {response.json().get('id')}")
            )
        else:
            # This will print the specific field causing the error
            self.stdout.write(self.style.ERROR(f"Failed: {response.text}"))
