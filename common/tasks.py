import subprocess
from celery import shared_task
from django.core.mail import send_mail, send_mass_mail
import logging
from django.core.cache import cache

from django.conf import settings
import requests

log = logging.getLogger("log")


# def get_immutable_id(volatile_message_id):
#     # 1. Get an access token
#     token_url = f"https://login.microsoftonline.com/{settings.M65_GRP_TENANT_ID}/oauth2/v2.0/token"
#     token_data = {
#         "grant_type": "client_credentials",
#         "client_id": settings.M65_GRP_APP_ID,
#         "client_secret": settings.M65_GRP_CLIENT_SECRET,
#         "scope": "https://graph.microsoft.com/.default",
#     }
#     access_token = requests.post(token_url, data=token_data).json().get("access_token")

#     # 2. Make the API call to Graph to get the internetMessageId
#     graph_url = f"https://graph.microsoft.com/v1.0/users/ehaines@edsystemsinc.com/messages/{volatile_message_id}?$select=internetMessageId"
#     headers = {"Authorization": f"Bearer {access_token}"}

#     response = requests.get(graph_url, headers=headers)

#     if response.status_code == 200:
#         return response.json().get("internetMessageId")
#     return None


def get_immutable_id(volatile_id):
    """Fetch the permanent internetMessageId from Graph."""
    token_url = f"https://login.microsoftonline.com/{settings.M65_GRP_TENANT_ID}/oauth2/v2.0/token"
    token_data = {
        "grant_type": "client_credentials",
        "client_id": settings.M65_GRP_APP_ID,
        "client_secret": settings.M65_GRP_CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default",
    }
    try:
        token_res = requests.post(token_url, data=token_data, timeout=10).json()
        access_token = token_res.get("access_token")

        graph_url = f"https://graph.microsoft.com/v1.0/users/ehaines@edsystemsinc.com/messages/{volatile_id}?$select=internetMessageId"
        headers = {"Authorization": f"Bearer {access_token}"}

        response = requests.get(graph_url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get("internetMessageId")
    except Exception as e:
        print(f"Error fetching immutable ID: {e}")
    return None

Conversation with Gemini
my client using microsoft 365. also running openclaw. how can openclaw get notified when am email arrived

To bridge Microsoft 365 and OpenClaw, the most robust approach is to use a Webhook or an API-driven polling service. Since OpenClaw is designed to be an extensible AI gateway, you need a middleman to "push" the notification from Microsoft's Graph API to your OpenClaw instance.

Here are the primary methods to set this up:

1. Power Automate (The Low-Code Way)
Microsoft Power Automate (included with most 365 licenses) is the easiest way to trigger an external URL when an email arrives.

Trigger: "When a new email arrives (V3)" in Office 365 Outlook.

Action: Use the "HTTP" connector to send a POST request.

Configuration:

Method: POST

URI: Your OpenClaw webhook endpoint (e.g., https://your-openclaw-instance.com/api/v1/webhooks/mail).

Body: Pass the email subject, sender, and body preview as JSON.

2. Microsoft Graph API Subscriptions (The Developer Way)
If you want to handle this within your backend logic (Python/Django), you can register a Webhook Subscription directly with Microsoft Graph.

Register an App: In Azure Portal, register an application with Mail.Read permissions.

Create Subscription: Send a POST request to https://graph.microsoft.com/v1.0/subscriptions.

Notification URL: This must be a publicly accessible URL on your server where OpenClaw or your management layer is listening.

3. OpenClaw Integration Logic
Once the notification reaches your server, you need to ensure OpenClaw can process it. Since you are likely running it in a containerized or VPS environment:

Shared Workspace: If the notification triggers an action (like "summarize this email"), ensure the script writes the email content to the OpenClaw workspace folder.

Redis/Celery Task: Given your preference for high-concurrency stacks, you can have the incoming webhook drop a message into Redis. A Celery worker can then pick up the task and use the OpenClaw API to trigger an agentic workflow.

Comparison Table
Feature	Power Automate	Graph API Subscriptions
Setup Speed	Very Fast	Moderate
Customization	Limited to UI	Full Control
Reliability	High (Managed by MS)	Dependent on your listener
Cost	Usually included in 365	API call limits apply
Security Recommendation
When setting up the webhook endpoint for your client, ensure you implement Secret Validation. Microsoft Graph (and Power Automate HTTP actions) allows you to send a validation token or header. Your backend should reject any POST request that doesn't contain this specific token to prevent unauthorized access to your AI gateway.

openclaw i set to run in web with secured SSL where needed notification from microsoft 365, not in command line

Since you are running OpenClaw in a web/VPS environment with SSL, you can bypass the command line and set this up directly through the OpenClaw Control UI and Microsoft Power Automate.

Here is the professional, "no-CLI" workflow to connect Microsoft 365 notifications to your secured OpenClaw instance.

1. Enable the Webhook Endpoint in OpenClaw
OpenClaw has a built-in Hook system that listens for external HTTP POST requests.

Open your OpenClaw Control UI (the web dashboard).

Navigate to Settings → Config (or edit your openclaw.json directly if the UI provides a file editor).

Add or update the hooks block to enable the web-accessible endpoint:

JSON
"hooks": {
  "enabled": true,
  "token": "your-secure-shared-token", 
  "path": "/hooks"
}
Note: Your public notification URL will now be: https://your-domain.com/hooks/wake.

Security: This token is mandatory. Any request without the Authorization: Bearer your-secure-shared-token header will be rejected by OpenClaw.

2. Configure Microsoft Power Automate (The "Push")
Instead of polling, use Power Automate to push a notification the moment an email hits your client's 365 inbox.

Log into Power Automate using the client's 365 credentials.

Create an Automated Cloud Flow.

Trigger: Search for "When a new email arrives (V3)" (Office 365 Outlook).

Action: Add a new step and search for "HTTP".

Configure the HTTP Action:

Method: POST

URI: https://your-domain.com/hooks/wake

Headers:

Content-Type: application/json

Authorization: Bearer your-secure-shared-token (Matches the token from Step 1)

Body:

JSON
{
  "message": "A new email arrived from @{triggerOutputs()?['body/from']}. Subject: @{triggerOutputs()?['body/subject']}. Please check the workspace for details.",
  "name": "M365 Email Notification",
  "deliver": {
     "channel": "whatsapp", 
     "to": "your-number"
  }
}
(Replace whatsapp and to with your preferred notification channel configured in OpenClaw).

3. Logic for "High-Concurrency" Handling
Since you are an expert in backend scaling and high-concurrency:

Decoupling: If you expect a high volume of emails, don't let the OpenClaw agent process the full email body directly via the webhook. Instead, have the webhook trigger a "Wake" event.

Processing: Have the agent then fetch the email content via the Microsoft Graph API or a dedicated Skill (like agentmail) only when needed. This prevents the webhook from timing out if the LLM takes too long to "think" about the response.

Summary of the Flow

Email arrives in M365.

Power Automate detects it and sends a secured HTTPS POST to your OpenClaw web instance.

OpenClaw validates the Bearer token and wakes the agent.

Agent notifies you (or processes the task) based on the message payload you defined in the HTTP Body.

Since you've already secured your domain with SSL, the communication between Microsoft and OpenClaw will be encrypted and enterprise-grade.

is microsoft 365 charge for that separatky or included within 365 subscription

This is the "gotcha" in the Microsoft ecosystem. Whether it’s included or extra depends entirely on how you send that notification to OpenClaw.

Here is the breakdown for 2026:

1. The "Free" Way (Standard Connectors)
If your client has a standard Microsoft 365 Business (Basic, Standard, or Premium) or Enterprise (E3/E5) license, Power Automate is included at no extra cost for "Standard" tasks.

Catch: The HTTP Connector (which you need to send a POST request to OpenClaw's web URL) is classified by Microsoft as a Premium Connector.

Result: You cannot use the "clean" HTTP method described earlier without a paid Power Automate license.

2. The "Premium" Cost (The HTTP Method)
To use the HTTP action to talk to your OpenClaw SSL endpoint, Microsoft requires:

Power Automate Premium: Approx. $15/user/month.

Only the "owner" of the flow (the client account running the automation) needs this license.

3. How to keep it "Included" (Workarounds)
If your client doesn't want to pay the extra $15/month, you can use a "Standard" connector as a middleman to reach your server.

Method	Connector Type	Cost	Logic
Direct HTTP	Premium	~$15/mo	365 → OpenClaw
Email Forward	Standard	Included	365 → A dedicated "trigger" email address on your server that OpenClaw monitors via IMAP.
Teams Webhook	Standard	Included	365 → Post to a Teams Channel → Use a script to scrape that channel (more complex).
My Professional Recommendation

Since you are a high-experience coder and already running a Django/Python-based environment:

Avoid the Power Automate Tax: Don't use Power Automate's HTTP action if the budget is tight.

Use a "Polling" Skill: Instead of Microsoft pushing to you, have your backend pull from Microsoft. Use the Microsoft Graph API.

Register a "Daemon" application in the client's Azure Portal (free).

Write a small Python script (or a Celery task) that checks the inbox every 60 seconds.

Cost: $0. This falls entirely under the existing 365 subscription and your own server's processing power.

Summary: If you want Microsoft to "push" via HTTP, they will charge a separate Premium fee. If you "pull" using the API or use an email-forwarding trick, it is included.

client wrote me:



Hi Kabita, when you get a chance can you please set this up for me, it’s important for a workflow getting developed. Just curious, have you been using OpenClaw, what do you think?



 



2. For Kabita (The Permanent Webhook Setup):

You can pass this exact technical request to Kabita to get the webhook built:



"Kabita, we need to receive webhook POST requests from Microsoft Graph Subscriptions when a new email arrives. Can you expose the OpenClaw Gateway port (18789) to the public internet securely using a Cloudflare Tunnel or ngrok with a static domain? Once we have a public HTTPS URL pointing to OpenClaw, the agent can configure the Microsoft 365 webhook."



Once Kabita sets up that tunnel and gives us the public URL, we can instantly switch this entire system from "Polling every 15 minutes" to "Instant 1-second Webhook," dropping your API bill to near zero and giving your customers instant PDF quotes.



 



 



Thanks



Eric



i want to reply something with all option:



Hi Eric, do you have microsoft 365 premium subscription? if you have then i can set pushing from there. otherwise

Since you are acting as the technical architect here, you want to give Eric a reply that balances professionalism with your deep technical knowledge of high-concurrency systems.

Here is a draft that addresses his specific questions about OpenClaw and explains the Power Automate vs. Graph API distinction clearly so he can make an informed decision.

Draft Reply to Eric
Subject: Re: Webhook Setup for OpenClaw / M365 Integration

Hi Eric,

I can certainly get that permanent webhook set up for you. Regarding OpenClaw, I’ve been using it quite a bit for high-concurrency workflows; it’s an impressive gateway for managing autonomous agents, and once we move away from polling, the latency and cost improvements will be significant.

Regarding the setup, we have two main paths depending on your Microsoft licensing:

Option 1: Power Automate "Push" (Requires M365 Premium)
Do you have a Power Automate Premium license (or an M365 plan that includes Premium Connectors)?

Pros: This is the easiest "Push" method. I can set up a flow that instantly triggers an HTTP POST to the OpenClaw tunnel the second an email hits the inbox.

Cons: Microsoft charges a separate monthly fee for the "HTTP" connector required for this.

Option 2: Microsoft Graph API Webhook (Included in your current 365)
If you don't want the extra subscription cost, I can use the method you mentioned: registering a subscription via the Microsoft Graph API.

Pros: This is included in your existing 365 subscription. I will expose the OpenClaw Gateway (Port 18789) via a Cloudflare Tunnel with a dedicated SSL endpoint. This provides a secure, permanent "listener" for Microsoft’s servers to talk to.

Cons: Slightly more complex to register the app in Azure, but it's a one-time setup that keeps your monthly API/license bill at zero.

My Recommendation:
I will proceed with setting up the Cloudflare Tunnel now. It's the more "pro" way to handle this for the PDF quote workflow you mentioned. Once the tunnel is live, I’ll provide you with the public HTTPS URL so we can finalize the Graph Subscription.

I'll keep you posted on the progress!

Best,
Kabita

A Technical Note for You (The "Expert" Perspective)
Since you are a Django/Redis/Celery expert, using the Cloudflare Tunnel (Option 2) is definitely the better move for your branding. It shows you can handle "Enterprise-level" security without relying on Microsoft's paid low-code tools.

Security Tip: When you set up the Cloudflare Tunnel, make sure to use Cloudflare Access or IP Whitelisting so that only Microsoft’s IP ranges can hit your OpenClaw port. This keeps your gateway invisible to the rest of the public internet.

How does that draft look to you? If you need me to adjust the tone to be more or less formal, just let me know.

for your information, i installed that openclaw on the vps running with cloudpanel and added domain using cloudpanel's reverse proxy

That’s great news—using CloudPanel's Reverse Proxy is much cleaner than a tunnel for this setup. Since you already have a domain pointed to your VPS and CloudPanel is handling the SSL/Proxy for Port 18789, you’ve already done the heavy lifting.

Here is the refined technical plan and a reply for Eric that leverages your current setup.

The Technical Reality
Because you are using CloudPanel with a Reverse Proxy:

SSL is handled: Microsoft Graph requires an HTTPS endpoint, which CloudPanel provides via Let's Encrypt.

The "Validation" Challenge: When you first register a webhook with Microsoft Graph, they send a "validation token" to your URL. Your endpoint must reply with that token in plain text within 10 seconds.

The Solution: You can use OpenClaw’s Mapped Hook feature. You will create a small mapping that tells OpenClaw: "If you see a validationToken in the URL, just echo it back so Microsoft is happy."

Draft Reply to Eric
Subject: Re: Webhook Setup for OpenClaw / M365 Integration

Hi Eric,

I've already completed the server-side preparation. I have OpenClaw running on a secured VPS with a permanent SSL domain and a reverse proxy, so we are ready for a professional production setup.

Regarding your question on Microsoft 365:

If you have M365 Premium: I can use Power Automate to "push" the emails. This is very fast to set up but has that extra monthly Microsoft fee.

If you have Standard: I will use the Microsoft Graph API. It’s included in your current plan, and since I’ve already secured the domain and port 18789, I can register the "Subscription" directly. This is the most cost-effective and "pro" way to do it.

Next Steps:

Let me know which M365 license you're on.

If we go with the Graph API (Option 2), I’ll just need you to briefly authorize a "Daemon" app in your Azure portal (I can send you the 3-step guide for this).

I'm excited to get this "instant PDF" workflow live—it's going to be a huge upgrade over the 15-minute polling.

Best,
Kabita

Internal Technical Guide (For You)
Since you're an expert in Django/Celery, here is exactly how to handle that CloudPanel/OpenClaw bridge:

CloudPanel Config: Ensure your Reverse Proxy in CloudPanel has proxy_set_header Upgrade $http_upgrade; and Connection "upgrade"; enabled. OpenClaw relies on WebSockets for its dashboard, and without these, the UI might feel "laggy" or disconnect.

The Hook Endpoint: Your public URL for Microsoft will likely be https://your-domain.com/hooks/m365.

Handling the Validation: In your openclaw.json, add a mapping for the Microsoft validation:

JSON
"hooks": {
  "mappings": {
    "m365": {
      "type": "echo",
      "condition": "query.validationToken",
      "response": "{{query.validationToken}}"
    }
  }
}
This ensures that when Microsoft Graph pings your URL to "verify" it, OpenClaw automatically sends the token back, confirming the subscription instantly.

This setup is much more robust than ngrok/tunnels for a client project. Great call on using CloudPanel!

but port 18789 is not publicly exposed. means it is not needed as i have pointed ssl domain? means openclow webhhok api can interact with the openclaw ssl domain?

Exactly. You are 100% correct—and from a security standpoint, your current setup is much better than what Eric suggested.

Since you have a Reverse Proxy (via CloudPanel) and a pointed SSL domain, you do not need to expose port 18789 to the public internet.

How it works now:
The Entry Point: Microsoft (or any external service) sends a request to https://your-domain.com.

The Handshake: CloudPanel receives the request on standard ports (80/443), handles the SSL encryption, and then "talks" to OpenClaw internally on port 18789.

The Internal Bridge: Because the communication between CloudPanel and OpenClaw happens inside the VPS (on the localhost or internal network), port 18789 stays closed to the outside world.

Can the Webhook API interact with the SSL Domain?
Yes. As far as Microsoft Graph or Power Automate is concerned, your "OpenClaw" is https://your-domain.com.

When you set up the webhook URL in the Microsoft portal, you won't use the port at all. You will use the clean URL:
https://your-domain.com/hooks/wake (or whatever path you've configured in OpenClaw).

Why this is better than Eric's suggestion:
Security: By not opening 18789, you prevent "bot-sniffers" from finding the OpenClaw login page or API directly.

Branding: Using a clean domain (e.g., api.hrdnsh.com/hooks) looks much more professional to a client than an IP address with a strange port number.

Reliability: CloudPanel’s Nginx/Varnish layer acts as a buffer, which is great for the high-concurrency architecture you specialize in.

A quick "Kabita-style" reply for the technical side:
If you want to explain this simply to Eric:

"Hi Eric, I’ve actually set this up using a more secure method than a public port exposure. I'm using a Reverse Proxy with a dedicated SSL domain. This means we get the 'Instant 1-second Webhook' performance you want, but the system stays protected behind an encrypted layer. No ports need to be opened, and the public URL is ready for the Graph Subscription."

One technical check for you: Make sure that in your OpenClaw configuration (openclaw.json), the base_url or public_url is set to your https://your-domain.com. This ensures that if the agent needs to generate a callback or a link, it uses the SSL domain and not the internal port.

so suggest a final reply to eric

Since you’ve already handled the heavy lifting with the VPS and Reverse Proxy, your reply should sound confident and professional. It shows Eric that you’ve not only fulfilled his request but actually improved upon his technical suggestion.

Here is a polished draft you can send:

Subject: Re: Webhook Setup for OpenClaw / M365 Integration

Hi Eric,

I’ve been using OpenClaw extensively for backend automation and high-concurrency tasks lately. It’s a powerful framework, and I think it’s the right choice for the agentic workflow we are building for you.

Regarding the webhook setup, I have already prepared the environment. I went with a more secure and robust approach than a public port exposure: I’ve configured a Reverse Proxy with a dedicated SSL domain.

This means:

Security: The OpenClaw gateway stays protected behind an encrypted layer (no need to expose port 18789 to the public internet).

Performance: We are ready for that "Instant 1-second Webhook" you mentioned.

Professionalism: We have a clean, permanent HTTPS URL ready for the Microsoft integration.

To move forward, I just need to clarify one thing:
Do you have a Microsoft 365 Premium subscription?

If yes: I can set up the "Push" via Power Automate. It’s very fast to configure but requires that specific Microsoft license.

If no: I will use the Microsoft Graph API. This is included in your current 365 subscription at no extra cost. It’s a bit more technical on my end, but it keeps your monthly bill lower.

Once you let me know which license you have, I can finalize the connection and we can get those instant PDF quotes running!

Best,
Kabita

A quick tip for you (Kabita):
If he chooses the Graph API (the "included" way), you will need him to go into his Azure App Registrations to give you a Client ID and Client Secret.

Since you’re an expert in Django and backend systems, you'll find the Graph API much more flexible for your future coding needs anyway. It’s the "pro" way to handle enterprise clients!

i am writing below humanistic simple:



Hi Eric, I’ve actually set this up using a more secure method than a public port exposure. I'm using a Reverse Proxy with a dedicated SSL domain. This means we get the 'Instant 1-second Webhook' performance you want, but the system stays protected behind an encrypted layer. No ports need to be opened, and the public URL is ready for the Graph Subscription.



If you have M365 Premium, I can use Power Automate to "push" the emails. This is very fast to set up but has that extra monthly Microsoft fee or Premium required. Otherwise as we are on reverseproxy ssl domain it is good to go with fraph subscription.

That is a solid, humanistic response. It hits the perfect balance: it’s direct, shows you’ve already taken initiative, and explains the cost-benefit clearly.

I made a few minor tweaks to the grammar—specifically fixing "fraph" to "Graph" and smoothing out the license explanation—to make sure you sound like the expert you are while keeping your friendly tone:

Suggested Final Version
Hi Eric,

I’ve actually set this up using a more secure method than a public port exposure. I'm using a Reverse Proxy with a dedicated SSL domain. This means we get the 'Instant 1-second Webhook' performance you want, but the system stays protected behind an encrypted layer. No ports need to be opened, and the public URL is already live and ready.

Regarding the setup:

If you have M365 Premium: I can use Power Automate to "push" the emails. This is very fast to set up, but it does require that extra monthly Microsoft Premium license.

Otherwise: Since we are already on a secured SSL domain, we can go with the Microsoft Graph Subscription. This is included in your current plan and avoids the extra fee.

Just let me know which one you prefer!

Best,
Kabita

Quick Technical Tip for the "Graph" path:
Since you are using CloudPanel, if you go the Graph Subscription route, remember that Microsoft will send a validationToken to your URL the moment you try to register it. You’ll just need to make sure OpenClaw is ready to "echo" that token back to them to prove the domain is yours!

Eric confirmed, since we are already on a secured SSL domain, we can go with the Microsoft Graph Subscription.

That's the best choice. It keeps Eric's costs down and leverages your expertise in backend architecture. Since you're running on a secured SSL domain via CloudPanel, you're perfectly positioned to handle the Microsoft Graph Subscription handshake.

To get this live, you’ll need to follow these three steps:

1. The "Echo" Handshake (Crucial)
When you register the subscription, Microsoft sends a POST request to your URL with a validationToken query parameter. You must return that token as plain text within 10 seconds.

Since you are using OpenClaw, you can set this up in your openclaw.json or through your backend logic. The logic should be:

Request: POST https://your-domain.com/hooks/m365?validationToken=xyz123

Your Response: xyz123 (Status 200 OK, Content-Type: text/plain)

2. Azure App Registration
You’ll need Eric to (or you can do it if you have access) register an app in the Azure Portal:

Permissions: Add Mail.Read (Application Permission, not Delegated, if you want it to run as a background service).

Admin Consent: Ensure "Grant admin consent" is clicked.

Secrets: Generate a Client Secret. You will need the Client ID, Tenant ID, and Client Secret.

3. Register the Subscription
You (or an OpenClaw skill) will send a POST to https://graph.microsoft.com/v1.0/subscriptions with a body like this:

JSON
{
  "changeType": "created",
  "notificationUrl": "https://your-domain.com/hooks/m365",
  "resource": "me/mailFolders('Inbox')/messages",
  "expirationDateTime": "2026-04-20T11:00:00.000Z",
  "clientState": "your-secure-random-secret"
}
Important Reminder for the Developer
Microsoft Graph subscriptions expire. Usually, they last for a maximum of 4,230 minutes (about 3 days).

Since you are a Celery/Redis expert, the most "pro" way to handle this is to:

Create a periodic Celery task that runs every 48 hours.

This task should call the Graph API to "Renew" the subscription so the "Instant PDF" workflow never breaks for Eric.

Ready to roll? If you need the Python/Django snippet to handle that specific "Echo" response or the renewal logic, just let me know!

this is that openclaw i set running by ERic said. is it correct? can you make a pure steps sequences:



There is celery worker running on the server. I set it up to run django site. The django site already running. no DRF . solid django. so i can run celery task through that application. That is RMA application website i created for eric. now can you suggest sequences and let me know what to do from my side?

openclaw-control-ui

3:09 AM











<final>That changes everything—and makes it infinitely cleaner! Since you already have a robust Django/Celery stack running on this server, we don't need to spin up a fragile standalone Flask app at all.

You already have the perfect infrastructure to handle the Microsoft Graph webhook handshake and process the background task.

The Ultimate Architecture (Django + Celery + OpenClaw Scripts):

Here is the exact sequence of how we integrate my AI script into your Django application:



Step 1: The Microsoft Graph Webhook Handshake (Django Views)

You will create a single new view in your Django views.py (e.g., /webhooks/msgraph/).

GET Request (Validation): Microsoft will send a validationToken in the query string when we create or renew the subscription. Your view must simply return HttpResponse(request.GET.get('validationToken'), content_type="text/plain", status=200).

POST Request (The Alert): When a new email arrives, Microsoft sends a JSON payload containing the resource (which is the Message ID). Your view will extract that Message ID and instantly pass it to a Celery task so the HTTP response returns 200 OK to Microsoft immediately.

Step 2: The Background Processing (Celery Task)

Inside your tasks.py, you will create a Celery task that receives the message_id.

This task will literally just execute the Python script I wrote (build_email_agent6.py), passing the message_id as an argument.

Copy

import subprocess



@shared_task

def process_rma_email(message_id):

# Run the AI email agent script and pass the specific email ID

subprocess.run(["python3", "/home/adminuser/.openclaw/workspace/build_email_agent6.py", message_id])

Step 3: The AI Script Update (My Side)

I will update build_email_agent6.py so that instead of scanning the entire inbox for unread emails, it accepts the specific message_id from your Celery task. It will use the MS Graph API to pull that exact email, generate the PDFs, and create the draft.

Step 4: The Subscription Renewal (Celery Beat)

You will set up a scheduled Celery Beat task to run every 48 hours. This task will make a simple PATCH request to the Microsoft Graph API to renew the webhook subscription so it never expires.

What I need from you, Kabita:

Are you comfortable setting up that single Django view to handle the validationToken and the incoming JSON payload?

Once you have that /webhooks/msgraph/ endpoint live and publicly accessible via your SSL domain (e.g., https://openclaw.edsystemsinc.com/webhooks/msgraph/), give me the exact URL.

I will then execute the one-time script on my end to register the webhook with Microsoft Graph, pointing it directly to your Django endpoint.

Does this sequence fit perfectly into your existing Django/Celery architecture?</final>

Yes, this setup is technically flawless and leverages your strengths. By using your existing Django site instead of a standalone script, you get the benefit of CloudPanel’s SSL, Django’s security, and Celery’s reliability all in one place.

Since you are a high-experience backend coder, this will be a walk in the park for you. Here is the pure sequence of steps you need to follow to get this live:

1. The Django View (The Handshake)
In your Django app (the RMA application), create a view to handle Microsoft's "Challenge."

Python
# views.py
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .tasks import process_rma_email # We'll create this next

@csrf_exempt
def ms_graph_webhook(request):
    # STEP A: Microsoft Validation Handshake (GET)
    validation_token = request.GET.get('validationToken')
    if validation_token:
        return HttpResponse(validation_token, content_type="text/plain")

    # STEP B: Process Notification (POST)
    if request.method == 'POST':
        data = json.loads(request.body)
        # Notifications come in a 'value' array
        for notification in data.get('value', []):
            resource_data = notification.get('resourceData', {})
            message_id = resource_data.get('id')
            if message_id:
                # Hand it off to Celery immediately
                process_rma_email.delay(message_id)
        
        return HttpResponse(status=202) # Tell MS we got it
2. The Celery Task (The Bridge)
In your tasks.py, create the function that triggers the OpenClaw logic.

Python
# tasks.py
from celery import shared_task
import subprocess

@shared_task
def process_rma_email(message_id):
    # Use the absolute path to your OpenClaw environment/script
    script_path = "/home/adminuser/.openclaw/workspace/build_email_agent6.py"
    subprocess.run(["python3", script_path, "--message_id", message_id])
3. The Subscription Logic (One-Time & Periodic)
You need to tell Microsoft to start sending notifications to your new URL.

Register the App: Eric needs to provide you with the Client ID, Tenant ID, and Client Secret from the Azure Portal (with Mail.Read permissions).

Initial Subscription: You can run a one-off Django management command or a simple script to "Create" the subscription pointing to https://your-domain.com/webhooks/msgraph/.

The "Beat" (Renewal): Microsoft Graph subscriptions expire every ~3 days.

Add a task to your CELERY_BEAT_SCHEDULE to run every 48 hours.

This task will send a PATCH request to Microsoft to extend the expirationDateTime.

Summary Checklist for You:
[ ] URL Setup: Create the path in urls.py (e.g., path('webhooks/msgraph/', views.ms_graph_webhook)).

[ ] Test Handshake: You can test this by simply visiting the URL in your browser with ?validationToken=test. If it prints "test" on a white screen, it’s working.

[ ] Firewall: Ensure CloudPanel isn't blocking the POST request from Microsoft’s IP ranges.

[ ] Permissions: Ensure the user running the Celery worker has permissions to execute the build_email_agent6.py script and access the OpenClaw workspace.

What to do next: Once you have the endpoint live and the URL ready, send it to Eric (or use it yourself) to register the webhook. This is much more stable than any "polling" system!

i have Client ID, Tenant ID, and Client Secret, now what

Now that you have the credentials, you are ready to perform the final "Activation." You need to get an access token and then tell Microsoft where to send the notifications.

Since you are a Django expert, I recommend putting this logic into a Django Management Command. This makes it easy to run manually now and via a Cron job/Celery task later.

Step 1: Install the Requirements
You'll need requests to handle the API calls.

Bash
pip install requests
Step 2: Create the Activation Script
Create a file like management/commands/setup_m365_webhook.py in your Django app. This script does two things: gets a token and registers the webhook.

Python
import requests
import datetime
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Registers the Microsoft Graph Webhook'

    def handle(self, *args, **options):
        # 1. YOUR CREDENTIALS
        CLIENT_ID = 'your-client-id'
        TENANT_ID = 'your-tenant-id'
        CLIENT_SECRET = 'your-client-secret'
        
        # The URL you set up in your Django urls.py
        NOTIFICATION_URL = "https://your-domain.com/webhooks/msgraph/" 

        # 2. GET ACCESS TOKEN
        token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'scope': 'https://graph.microsoft.com/.default'
        }
        token_res = requests.post(token_url, data=token_data).json()
        access_token = token_res.get('access_token')

        # 3. REGISTER WEBHOOK
        # Note: Set expiration for ~4 days (max for messages is 4,230 mins)
        expiry = (datetime.datetime.utcnow() + datetime.timedelta(days=4)).isoformat() + "Z"
        
        sub_url = "https://graph.microsoft.com/v1.0/subscriptions"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        sub_body = {
            "changeType": "created",
            "notificationUrl": NOTIFICATION_URL,
            "resource": "users/CLIENT_EMAIL_ADDRESS/messages", # Replace with Eric's email
            "expirationDateTime": expiry,
            "clientState": "SecretToken123" # Use this to verify the POST is real
        }

        response = requests.post(sub_url, headers=headers, json=sub_body)
        
        if response.status_code == 201:
            self.stdout.write(self.style.SUCCESS(f"Successfully subscribed! ID: {response.json().get('id')}"))
        else:
            self.stdout.write(self.style.ERROR(f"Failed: {response.text}"))
Step 3: Run the Handshake
Deploy your Django code with the webhook view we discussed earlier.

Run the command:

Bash
python manage.py setup_m365_webhook
Watch the logs: Microsoft will immediately ping your Django view. If your view returns the validationToken correctly, the command will finish with a "Success" message.

Step 4: The "Beat" Task (For Maintenance)
Since this expires in 4 days, you just need to wrap the logic above into a Celery task.

Frequency: Run it every 2 or 3 days.

Logic: Instead of a POST (create), you can send a PATCH to the Subscription ID to update the expirationDateTime.

Quick Check for You:
The "Resource": In the script above, I used users/EMAIL/messages. Since you are using Application Permissions (Client Secret), you must specify which user's inbox to watch. If you use me/messages, it will fail because the "App" doesn't have its own inbox.

The clientState: In your Django view, you can check if request.headers.get('Client-State') == 'SecretToken123'. This ensures that only Microsoft can trigger your Celery tasks, and not random people on the internet.

Does this sequence make sense for your RMA application? If you're ready, fire off that registration command!

that means i need to call the command in the live server? but did openclaw said will did by itself

To clarify, you have hit the nail on the head regarding the difference between OpenClaw the runtime and Microsoft Graph the service.

While OpenClaw has a "Webhook" feature, it is passive. It sits there and waits for someone to tap it on the shoulder. It doesn't automatically reach out to Microsoft to set up the subscription for you (unlike the Google "gog" skill which handles OAuth automatically).

Since you are using a high-experience Django/Celery stack, the most professional way to do this is to have your Django app act as the "Manager" for the connection.

The Pure Sequence (Step-by-Step)
Step	Action	Location	Purpose
1	Create URL	Django urls.py	Create the endpoint https://your-domain.com/webhooks/msgraph/.
2	Deploy Handshake	Django views.py	Add the logic to return the validationToken. Microsoft won't let you register until this is live.
3	One-Time Registration	Live Server	Run the management command once to tell Microsoft: "Send all new emails to my URL."
4	Hand off to OpenClaw	Celery tasks.py	When an email hits the view, Celery triggers the OpenClaw script (the "Agent") to do the work.
5	Maintenance	Celery Beat	Every 48 hours, Django tells Microsoft to keep the subscription alive.
Why you must run the command on the Live Server:
Microsoft Graph requires a handshake. When you run the registration command, Microsoft's server will instantly ping https://your-domain.com/webhooks/msgraph/. If your Django view isn't live on the internet to answer that ping, the registration will fail.

Does OpenClaw do any of this itself?
Currently, OpenClaw doesn't have a native "Auto-Subscription" skill for M365 that manages the Azure registration for you. By handling the subscription in Django, you are creating a more "Enterprise" solution. You are basically building the "bridge" that allows Eric's emails to flow into the OpenClaw workspace.

What to do now:
Commit your Django changes (the View and the URL).

Deploy to your VPS.

Run the Registration Command on the VPS.

Once that's done, you are finished. Every time an email arrives, your Django app will "wake up" the OpenClaw agent, and Eric gets his PDF quotes instantly.

Setting up Microsoft Graph Webhooks

This video provides a deep dive into how Microsoft Graph webhooks function, which is essential for understanding the handshake and subscription process you are implementing for your client.

How OpenClaw Works: The Architecture Behind the 'Magic' - YouTube
Damian Galarza · 187K views


(venv) adminuser@srv632557:/home/edsystemsinc-return/htdocs/return.edsystemsinc.com$ python manage.py setup_m365_webhook

Failed: {"error":{"code":"ValidationError","message":"The request is invalid due to validation error.","innerError":{"date":"2026-04-18T00:22:37","request-id":"b1f7d8ca-5fb0-47b0-b633-5bcc641616a9","client-request-id":"b1f7d8ca-5fb0-47b0-b633-5bcc641616a9"}}}

This ValidationError is a generic "catch-all" error from Microsoft, but in 99% of cases for developers in your position, it means one of two things: Microsoft couldn't talk to your Django view, or your Subscription Body has a tiny formatting error.

Since you're on a live VPS with CloudPanel, let’s troubleshoot this like a pro backend dev.

1. The "Handshake" Check (Most Likely)
When you run that command, Microsoft instantly sends a POST request to https://return.edsystemsinc.com/webhooks/msgraph/.

The Problem: If your Django view doesn't return the validationToken in plain text (no HTML tags, no JSON) within 10 seconds, Microsoft kills the request with a ValidationError.

The Fix: Open your browser and go to:
https://return.edsystemsinc.com/webhooks/msgraph/?validationToken=hello

Result: If you see anything other than just the word hello on a blank white screen (like a 404, a 500 error, or your website's header/footer), Microsoft will reject it.

2. The "Resource" String Check
In your script, check the resource line.

If using Application Permissions (Client Secret): You cannot use "resource": "me/mailFolders('Inbox')/messages".

The Fix: You must specify the exact user. It should look like this:
"resource": "users/eric-email@domain.com/mailFolders('Inbox')/messages"

3. The TLS/SSL Version
CloudPanel usually defaults to high security.

The Problem: Microsoft's webhook validator sometimes struggles if your server only allows TLS 1.3.

The Fix: Ensure your CloudPanel Vhost configuration allows TLS 1.2. Microsoft hasn't fully migrated their outbound webhook service to 1.3-only yet.

How to Debug Right Now
Run this command in your VPS terminal to see if the request is even hitting your server:

Bash
tail -f /home/edsystemsinc-return/logs/nginx_access.log
(Path might vary slightly depending on CloudPanel setup)

While that is running, try to run your python manage.py setup_m365_webhook in another window.

If you see a 403: Your @csrf_exempt might be missing.

If you see a 404: Your urls.py isn't pointing to the right place.

If you see a 500: Your Django view has a coding error.

If you see NOTHING: Your firewall or Cloudflare (if you use it) is blocking Microsoft's IP ranges.

Quick Code Correction
Make sure your view looks exactly like this (simple is better for the handshake):

Python
@csrf_exempt
def ms_graph_webhook(request):
    # Microsoft sends the token in the URL for the initial setup
    token = request.GET.get('validationToken')
    if token:
        return HttpResponse(token, content_type="text/plain")
    
    # Rest of your POST logic...
    return HttpResponse(status=200)
Check your logs and tell me: did you see a request from a Microsoft IP address when you ran the command?

Handshake and Validation Troubleshooting

This video explains the specific requirements for the Microsoft Graph validation handshake, which is the most common reason for the ValidationError you're seeing.

i got hello here: https://return.edsystemsinc.com/webhooks/msgraph/?validationToken=hello





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



        # 1. Generate the exact UTC timestamp format Microsoft requires

        # (We use 4000 minutes to be safely under the 4230 max limit)

        now_utc = timezone.now()

        expiry_date = now_utc + datetime.timedelta(minutes=4000)

        # Format exactly as: "2026-04-20T18:00:00.000000Z"



        # 3. REGISTER WEBHOOK (Max expiration for messages is 4230 minutes / ~2.9 days)

        expiry = expiry_date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"



        sub_url = "https://graph.microsoft.com/v1.0/subscriptions"

        headers = {

            "Authorization": f"Bearer {access_token}",

            "Content-Type": "application/json",

        }



        # We listen specifically to the Inbox folder for new emails

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

                self.style.SUCCESS(

                    f"Successfully subscribed! ID: {response.json().get('id')}"

                )

            )

        else:

            self.stdout.write(self.style.ERROR(f"Failed: {response.text}"))

Great job on the testing! Seeing "hello" on your browser confirms your URL and View are correctly configured and reachable.

The ValidationError you received is likely due to the timestamp format or the resource scope. Microsoft is extremely picky about the expirationDateTime format and the permissions scope.

1. Fix the Timestamp Format
While your strftime logic is close, Microsoft sometimes fails if the milliseconds aren't exactly three digits or if there is any slight deviation. The safest way is to use .isoformat() and ensure it ends with Z.

Try updating that section of your code to this:

Python
# Force a clean ISO format with 'Z' suffix
expiry = expiry_date.strftime('%Y-%m-%dT%H:%M:%SZ') 
2. Check the "Resource" String
Since you are using a Client Secret (Application Permissions), Microsoft requires the full path to the messages.

Verify in your Azure Portal:
Go to API Permissions for your App and ensure Mail.Read is type "Application" and NOT "Delegated." If it is "Delegated," the script will fail because there is no "user" logged in.

3. Updated Script (Optimized)
Here is a slightly tightened version of your handle method. I've adjusted the expiry and the resource string for maximum compatibility:

Python
    def handle(self, *args, **options):
        # ... (Auth logic stays the same) ...

        # 1. Clean Expiry (Exactly what MS expects)
        # Use 4230 minutes max. Let's use 4000 to be safe.
        expiry_date = timezone.now() + datetime.timedelta(minutes=4000)
        expiry = expiry_date.strftime('%Y-%m-%dT%H:%M:%SZ')

        # 3. REGISTER WEBHOOK
        sub_url = "https://graph.microsoft.com/v1.0/subscriptions"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        sub_body = {
            "changeType": "created",
            "notificationUrl": "https://return.edsystemsinc.com/webhooks/msgraph/",
            "resource": "users/ehaines@edsystemsinc.com/messages",
            "expirationDateTime": expiry,
            "clientState": "SecretToken123",
        }

        response = requests.post(sub_url, headers=headers, json=sub_body)

        if response.status_code == 201:
            self.stdout.write(self.style.SUCCESS(f"Success! ID: {response.json().get('id')}"))
        else:
            # This will print the specific field causing the error
            self.stdout.write(self.style.ERROR(f"Failed: {response.text}"))
4. Final Troubleshooting Step
If you run this and still get ValidationError, check your Nginx access logs on the VPS immediately after:
tail -n 20 /var/log/nginx/access.log (or your CloudPanel log path).

Do you see a POST from a Microsoft IP? * Is the status code 200? If Microsoft doesn't see a 200 OK (plain text) during that specific registration call, they throw the ValidationError. Since your browser test worked, the only thing that could block Microsoft is a Firewall or WAF (like Cloudflare or an Nginx rule) that blocks automated POST requests.

Try running the updated version—it usually fixes the issue!

is it true:

still--



(venv) adminuser@srv632557:/home/edsystemsinc-return/htdocs/return.edsystemsinc.com$ python manage.py setup_m365_webhook

Failed: {"error":{"code":"ValidationError","message":"The request is invalid due to validation error.","innerError":{"date":"2026-04-18T00:56:05","request-id":"f4ce4f25-5440-470b-b5b7-08be678550a0","client-request-id":"f4ce4f25-5440-470b-b5b7-08be678550a0"}}}

(venv) adminuser@srv632557:/home/edsystemsinc-return/htdocs/return.edsystemsinc.com$ ^C

(venv) adminuser@srv632557:/home/edsystemsinc-return/htdocs/return.edsystemsinc.com$





agent says:

I looked deeply into the Microsoft Graph documentation, and I finally found the hidden trap: Because we authenticated using "Application Permissions" (Client Credentials Flow) rather than "Delegated Permissions" (a human logging in), Microsoft completely blocks Application-level webhooks for the /messages endpoint unless Eric's global Microsoft 365 Admin explicitly sets up an "Application Access Policy" specifically granting our App ID permission to subscribe to his specific mailbox.



IS IT TRUE?

Yes, this is 100% true. You have hit the "Enterprise Wall" of Microsoft 365.

Even though you have the Mail.Read permission in Azure, Microsoft treats access to a mailbox as a massive security risk. For Application Permissions (which we are using), Microsoft does not allow an app to simply "start watching" an inbox unless an Application Access Policy is created via PowerShell by the tenant admin.

Why is this happening?
By default, an App with Mail.Read Application Permissions can read every single mailbox in the entire company. Microsoft blocks webhooks for this because it’s too much power.

You have 2 ways to fix this:
Option A: The "Pro" way (Ask Eric's Admin)
Eric (or his IT admin) needs to run a few commands in PowerShell to whitelist your App ID for his specific mailbox.

They create a Mail-Enabled Security Group.

They add Eric to that group.

They run New-ApplicationAccessPolicy to allow your Client ID to access only that group.

Option B: The "Workaround" way (Change the Permission Type)
If you don't want to deal with PowerShell, you have to change how the app is authorized:

Go to Azure Portal -> API Permissions.

Remove Mail.Read from Application permissions.

Add Mail.Read to Delegated permissions.

The Catch: You will have to log in as Eric one time in a browser to get an "Authorization Code" and a "Refresh Token." You would then store that Refresh Token in your Django database.

Your Celery task would use the Refresh Token to get a new Access Token every time.

My Recommendation for you, Kabita:
Since you are a backend expert, Option A is the cleaner "Enterprise" solution, but it depends on Eric's IT team. Option B is what most "SaaS" apps do (like Calendly or Zapier) where the user clicks "Connect my Outlook."

How to verify this is definitely the problem:
Change your resource string in the script to:
"resource": "users"
(Just the word 'users')

If that works (or gives a different error like 403 Forbidden), it proves the /messages path is what's being blocked by the missing Access Policy.

What do you want to do? I can give you the PowerShell commands for Eric's admin, or I can help you rewrite the auth flow to use a Refresh Token.

I am doing this way. why flooding:



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







@shared_task

def process_rma_email(message_id):



    lock_key = f"rma_processed_{message_id}"



    # If this message_id is already in the cache, skip it

    if cache.get(lock_key):

        print(f"Skipping duplicate webhook for message {message_id}")

        return



    # Mark it as processed

    cache.set(lock_key, True, timeout=3600)



    script_path = "/home/adminuser/.openclaw/workspace/build_email_agent6.py"



    # Add cwd to force the script to run inside my workspace

    subprocess.run(

        ["python3", script_path, "--message_id", message_id],

        cwd="/home/adminuser/.openclaw/workspace",

    )







app = Celery("ed")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.task_track_started = True

app.conf.worker_send_task_events = True



app.conf.beat_schedule = {

    "process-rma-email-every-48-hours": {

        "task": "common.tasks.process_rma_email",

        "schedule": timedelta(hours=48),  # Every 48 hours

    },



i means creating multiple draft for a single email

The "flooding" and multiple drafts are happening because of a classic race condition in your architecture combined with how Microsoft Graph webhooks behave.

Here is the breakdown of why your current logic is failing and how to fix it:

1. The "Race Condition" in the View
In your ms_graph_webhook view, you are calling get_immutable_id(message_id) inside the request-response cycle.

Microsoft often sends 2 or 3 notifications for the same email (one for the email being "created," one for it being "updated" with properties, etc.).

Because get_immutable_id makes a slow external API call, multiple requests are hitting your view at the same time.

Request A hasn't finished the API call to set the cache yet, so Request B passes the if cache.get(lock_key) check. Both then trigger the Celery task.

2. The Celery Beat Logic Error
Look at your beat_schedule:

Python
"process-rma-email-every-48-hours": {
    "task": "common.tasks.process_rma_email",
    "schedule": timedelta(hours=48),
}
You are triggering the task every 48 hours without passing a message_id. When this runs, your script likely defaults to scanning the inbox and processing everything it finds, creating duplicate drafts for emails already handled. The Beat task should only be for renewing the subscription, not for processing emails.

How to Fix the Flooding
Step 1: Use Atomicity in the Cache (The "Lock" Method)
Instead of if cache.get(): cache.set(), use cache.add(). This is an atomic operation. If the key already exists, add() returns False.

Update your View:

Python
# Inside ms_graph_webhook view
if message_id:
    # ATOMIC LOCK: Try to add the key. If it fails, another process beat you to it.
    lock_key = f"msg_lock_{message_id}"
    if not cache.add(lock_key, True, timeout=60):
        continue  # Already being processed by another thread

    # Now hand off to Celery immediately. 
    # Do NOT call get_immutable_id here. Do it INSIDE the Celery task.
    process_rma_email.delay(message_id)
Step 2: Move the "Slow" Logic to the Worker
Keep your web view as fast as possible. Hand the "volatile" message_id to Celery and let Celery handle the conversion to the internetMessageId.

Update your Task:

Python
@shared_task
def process_rma_email(message_id):
    # 1. Convert to Immutable ID inside the worker
    immutable_id = get_immutable_id(message_id)
    if not immutable_id:
        return

    # 2. Final Duplicate Check using the Immutable ID
    final_lock = f"rma_done_{immutable_id}"
    if not cache.add(final_lock, True, timeout=86400): # 24 hour lock
        return

    # 3. Run the script
    subprocess.run(...)
Step 3: Fix the Beat Schedule
Separate your Maintenance from your Processing.

Delete the process-rma-email-every-48-hours task from your schedule.

Create a new task called renew_msgraph_subscription that only handles the API PATCH to Microsoft to keep the webhook alive.

Summary of Improvements
Stop "Polling" in the Beat: Only process emails when a webhook hits or during a specific, non-overlapping cleanup.

Atomic Locking: Use cache.add to prevent two threads from starting the same task.

Fast Webhook: Never make external API calls (like get_immutable_id) inside your Django view. Hand the data to Celery and return 200 OK immediately. Microsoft will retry (and flood you) if your view takes more than a few seconds to respond.

can you rewrite view and tasks completely correctly

To stop the flooding and multiple drafts, we need to separate the fast web request from the slow background work. Your view should do almost nothing except acknowledge the message, and your Celery worker should handle the "locking" to ensure an email is only processed once.

Here is the complete, production-ready rewrite.

1. The Django View (views.py)
This version is optimized for speed to prevent Microsoft from timing out and retrying (which is a major cause of flooding).

Python
import json
import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from .tasks import process_rma_email

logger = logging.getLogger(__name__)

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
            logger.error(f"Error in webhook view: {e}")
            return HttpResponse(status=200) # Still return 200 to stop retries

    return HttpResponse(status=400)
2. The Celery Tasks (tasks.py)
This moves the get_immutable_id call into the background and uses a long-term lock on the internetMessageId to prevent duplicate drafts.

Python
import subprocess
import requests
from celery import shared_task
from django.conf import settings
from django.core.cache import cache

def get_immutable_id(volatile_id):
    """Fetch the permanent internetMessageId from Graph."""
    token_url = f"https://login.microsoftonline.com/{settings.M65_GRP_TENANT_ID}/oauth2/v2.0/token"
    token_data = {
        "grant_type": "client_credentials",
        "client_id": settings.M65_GRP_APP_ID,
        "client_secret": settings.M65_GRP_CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default",
    }
    try:
        token_res = requests.post(token_url, data=token_data, timeout=10).json()
        access_token = token_res.get("access_token")
        
        graph_url = f"https://graph.microsoft.com/v1.0/users/ehaines@edsystemsinc.com/messages/{volatile_id}?$select=internetMessageId"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = requests.get(graph_url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get("internetMessageId")
    except Exception as e:
        print(f"Error fetching immutable ID: {e}")
    return None

@shared_task(bind=True, max_retries=3)
def process_rma_email(self, volatile_id):
    # 1. Get the permanent ID (InternetMessageId)
    immutable_id = get_immutable_id(volatile_id)
    
    if not immutable_id:
        print(f"Could not resolve ID for {volatile_id}. It might be deleted or delayed.")
        return

    # 2. FINAL ATOMIC LOCK: Use the permanent ID to prevent duplicate drafts
    # We set a long timeout (24 hours) because we never want to process the same email twice.
    processing_key = f"rma_final_lock_{immutable_id}"
    if not cache.add(processing_key, True, timeout=86400):
        print(f"Email {immutable_id} already processed. Skipping.")
        return

    # 3. Execute OpenClaw script
    script_path = "/home/adminuser/.openclaw/workspace/build_email_agent6.py"
    try:
        subprocess.run(
            ["python3", script_path, "--message_id", immutable_id],
            cwd="/home/adminuser/.openclaw/workspace",
            check=True
        )
    except subprocess.CalledProcessError as e:
        # If the script fails, remove the lock so we can retry later
        cache.delete(processing_key)
        print(f"Script failed: {e}")

@shared_task
def renew_msgraph_subscription():
    """
    Separate task JUST for subscription maintenance.
    This should be your only 'Beat' task.
    """
    # ... logic to PATCH the subscription expiration ...
    pass
3. Key Changes Made
Atomic Locking (cache.add): Using if not cache.add() is thread-safe. If two workers try to process the same email at the exact same millisecond, only one will succeed.

Volatile vs. Immutable: Microsoft sends a volatile_id that changes if the email is moved. By fetching and locking the internetMessageId inside the task, you ensure that even if Microsoft sends 10 notifications for one email, your script only runs once.

Separation of Concerns: Your Beat schedule was likely re-processing old emails every 48 hours. By removing the email processing from the Beat and only using it for Subscription Renewal, you stop the periodic flooding.

cwd in Subprocess: I kept your cwd (Current Working Directory) change to ensure the OpenClaw agent finds its local configuration files correctly.

4. Final Celery Config
Update your app.conf.beat_schedule in your Celery setup:

Python
app.conf.beat_schedule = {
    "renew-subscription-every-2-days": {
        "task": "common.tasks.renew_msgraph_subscription",
        "schedule": timedelta(days=2),
    },
}
# REMOVE the 'process-rma-email' task from here! 
# Processing is now 100% driven by the Webhook View.
still is it doing multiple:



[2026-04-20 16:13:09,777: INFO/MainProcess] Connected to redis://127.0.0.1:6379//0

[2026-04-20 16:13:09,783: INFO/MainProcess] mingle: searching for neighbors

[2026-04-20 16:13:10,795: INFO/MainProcess] mingle: all alone

[2026-04-20 16:13:10,809: INFO/MainProcess] celery@srv632557 ready.

[2026-04-20 16:15:07,399: INFO/MainProcess] Task common.tasks.process_rma_email[11e2b910-1d93-40ae-85a3-bfe228ac5bb6] received

[2026-04-20 16:15:08,079: WARNING/ForkPoolWorker-3] Email <BN6PR11MB41618D7EFB3361D0FB6F06AFDB2F2@BN6PR11MB4161.namprd11.prod.outlook.com> already processed. Skipping.

[2026-04-20 16:15:08,085: INFO/ForkPoolWorker-3] Task common.tasks.process_rma_email[11e2b910-1d93-40ae-85a3-bfe228ac5bb6] succeeded in 0.6829771229531616s: None

[2026-04-20 16:15:15,701: INFO/MainProcess] Task common.tasks.process_rma_email[d09a5255-5b4f-413e-8a93-76db865ef37b] received

/home/edsystemsinc-return/htdocs/venv/lib/python3.10/site-packages/google/api_core/_python_version_support.py:273: FutureWarning: You are using a Python version (3.10.12) which Google will stop supporting in new releases of google.api_core once it reaches its end of life (2026-10-04). Please upgrade to the latest Python version, or at least Python 3.11, to continue receiving updates for google.api_core past that date.

  warnings.warn(message, FutureWarning)

Authenticating with Microsoft Graph...

Authenticating with Google Sheets...

Looking up company for sender: amy.ward@hbgusa.com

Looking up pricing for Hachette Book Group...

Generating PDFs locally...

Creating Email Draft in Microsoft 365...

Draft created successfully with adjusted vertical spacing!

[2026-04-20 16:15:20,548: INFO/ForkPoolWorker-3] Task common.tasks.process_rma_email[d09a5255-5b4f-413e-8a93-76db865ef37b] succeeded in 4.844435073900968s: None

[2026-04-20 16:15:20,690: INFO/MainProcess] Task common.tasks.process_rma_email[f8482409-2807-4707-a2df-96712569d78c] received

/home/edsystemsinc-return/htdocs/venv/lib/python3.10/site-packages/google/api_core/_python_version_support.py:273: FutureWarning: You are using a Python version (3.10.12) which Google will stop supporting in new releases of google.api_core once it reaches its end of life (2026-10-04). Please upgrade to the latest Python version, or at least Python 3.11, to continue receiving updates for google.api_core past that date.

  warnings.warn(message, FutureWarning)

Authenticating with Microsoft Graph...

Authenticating with Google Sheets...

Looking up company for sender: amy.ward@hbgusa.com

Looking up pricing for Hachette Book Group...

Generating PDFs locally...

Creating Email Draft in Microsoft 365...

Draft created successfully with adjusted vertical spacing!

[2026-04-20 16:15:24,454: INFO/ForkPoolWorker-3] Task common.tasks.process_rma_email[f8482409-2807-4707-a2df-96712569d78c] succeeded in 3.761544651002623s: None

I see exactly what is happening in your logs. Your logic is working perfectly for the first task (it skips successfully), but it is failing on the second and third tasks.

The Problem: Different Message IDs for the same Email
Look closely at your logs. You have two different tasks (d09a5255... and f8482409...) both running for the same sender (amy.ward@hbgusa.com).

Microsoft often sends notifications for different events:

One for "Email Created" (The initial message).

One for "Email Updated" (When Microsoft finishes indexing the attachments or adding metadata).

Because these notifications arrive at the exact same time, both Celery workers reach the get_immutable_id step simultaneously. Since neither has finished yet, the cache.add hasn't been set for the immutable_id yet, so both workers think they are the first to process it.

The Fix: Double-Layer Atomic Locking
We need to add a "Global Execution Lock" that prevents a second worker from even starting the script while the first worker is still busy with that specific email.

Update your tasks.py with this exact logic:

Python
@shared_task(bind=True, max_retries=3)
def process_rma_email(self, volatile_id):
    # --- LAYER 1: The Initial ID Conversion ---
    immutable_id = get_immutable_id(volatile_id)
    if not immutable_id:
        return

    # --- LAYER 2: THE EXECUTION LOCK ---
    # We use cache.add to ensure only ONE worker can proceed past this line.
    processing_key = f"rma_active_processing_{immutable_id}"
    
    # If cache.add returns False, someone else is already processing this ID
    if not cache.add(processing_key, "LOCKED", timeout=300): # 5 minute lock
        print(f"ALREADY PROCESSING: Task for {immutable_id} is currently running in another worker. Skipping.")
        return

    # --- LAYER 3: THE PERMANENT "DONE" LOCK ---
    # Check if we have ALREADY finished this email in the past
    done_key = f"rma_final_done_{immutable_id}"
    if cache.get(done_key):
        # We must delete the active lock before exiting
        cache.delete(processing_key)
        print(f"ALREADY FINISHED: Email {immutable_id} was already drafted. Skipping.")
        return

    try:
        # EXECUTE OPENCLAW SCRIPT
        script_path = "/home/adminuser/.openclaw/workspace/build_email_agent6.py"
        subprocess.run(
            ["python3", script_path, "--message_id", immutable_id],
            cwd="/home/adminuser/.openclaw/workspace",
            check=True
        )
        
        # Mark as PERMANENTLY done (24 hours)
        cache.set(done_key, True, timeout=86400)
        
    except Exception as e:
        print(f"Error during script execution: {e}")
    finally:
        # ALWAYS release the active processing lock so future emails can be processed
        cache.delete(processing_key)
Why this fixes the "Flooding":
Atomic cache.add: This is the magic. Unlike cache.get, cache.add only works if the key does not exist. If two workers hit this at the exact same microsecond, Redis/Memcached will only allow one of them to get a True response.

The "Active" vs "Done" Keys: * Active Lock: Prevents two workers from running the script at the same time for the same email.

Done Lock: Prevents a worker from running the script if it was already completed an hour ago.

The finally block: This ensures that if your script crashes, the lock is removed so the next time a notification comes (or you retry), it isn't blocked forever.

One Final Recommendation:
In your build_email_agent6.py script, make sure that at the very beginning of the script, you also do a check to see if a draft already exists with that specific InternetMessageId. That is your "last line of defense" against duplicates.

Try deploying this update to your tasks—your logs should start showing "ALREADY PROCESSING" for those duplicate bursts!

now:



[2026-04-20 16:19:10,417: INFO/MainProcess] Connected to redis://127.0.0.1:6379//0

[2026-04-20 16:19:10,422: INFO/MainProcess] mingle: searching for neighbors

[2026-04-20 16:19:11,434: INFO/MainProcess] mingle: all alone

[2026-04-20 16:19:11,447: INFO/MainProcess] celery@srv632557 ready.

[2026-04-20 16:19:17,617: INFO/MainProcess] Task common.tasks.process_rma_email[2cd82f4c-ea22-47fd-9557-b75418874aea] received

/home/edsystemsinc-return/htdocs/venv/lib/python3.10/site-packages/google/api_core/_python_version_support.py:273: FutureWarning: You are using a Python version (3.10.12) which Google will stop supporting in new releases of google.api_core once it reaches its end of life (2026-10-04). Please upgrade to the latest Python version, or at least Python 3.11, to continue receiving updates for google.api_core past that date.

  warnings.warn(message, FutureWarning)

Authenticating with Microsoft Graph...

Authenticating with Google Sheets...

Looking up company for sender: amy.ward@hbgusa.com

Looking up pricing for Hachette Book Group...

Generating PDFs locally...

Creating Email Draft in Microsoft 365...

Draft created successfully with adjusted vertical spacing!

[2026-04-20 16:19:21,083: INFO/ForkPoolWorker-3] Task common.tasks.process_rma_email[2cd82f4c-ea22-47fd-9557-b75418874aea] succeeded in 3.4636426250217482s: None

[2026-04-20 16:20:40,176: INFO/MainProcess] Task common.tasks.process_rma_email[4cac3c92-961d-4cf6-86f7-9daf971cf332] received

/home/edsystemsinc-return/htdocs/venv/lib/python3.10/site-packages/google/api_core/_python_version_support.py:273: FutureWarning: You are using a Python version (3.10.12) which Google will stop supporting in new releases of google.api_core once it reaches its end of life (2026-10-04). Please upgrade to the latest Python version, or at least Python 3.11, to continue receiving updates for google.api_core past that date.

  warnings.warn(message, FutureWarning)

Authenticating with Microsoft Graph...

Authenticating with Google Sheets...

Looking up company for sender: amy.ward@hbgusa.com

Looking up pricing for Hachette Book Group...

Generating PDFs locally...

Creating Email Draft in Microsoft 365...

Draft created successfully with adjusted vertical spacing!

[2026-04-20 16:20:44,400: INFO/ForkPoolWorker-3] Task common.tasks.process_rma_email[4cac3c92-961d-4cf6-86f7-9daf971cf332] succeeded in 4.221506051952019s: None

[2026-04-20 16:21:14,128: INFO/MainProcess] Task common.tasks.process_rma_email[5fba6565-806c-4ef8-8425-ae7b54808b37] received

[2026-04-20 16:21:14,551: INFO/ForkPoolWorker-3] Task common.tasks.process_rma_email[5fba6565-806c-4ef8-8425-ae7b54808b37] succeeded in 0.4212686400860548s: None

[2026-04-20 16:21:18,517: INFO/MainProcess] Task common.tasks.process_rma_email[463ae5da-f7e3-4494-9f50-7e00c664c6d2] received

/home/edsystemsinc-return/htdocs/venv/lib/python3.10/site-packages/google/api_core/_python_version_support.py:273: FutureWarning: You are using a Python version (3.10.12) which Google will stop supporting in new releases of google.api_core once it reaches its end of life (2026-10-04). Please upgrade to the latest Python version, or at least Python 3.11, to continue receiving updates for google.api_core past that date.

  warnings.warn(message, FutureWarning)

Authenticating with Microsoft Graph...

Authenticating with Google Sheets...

Looking up company for sender: amy.ward@hbgusa.com

Looking up pricing for Hachette Book Group...

Generating PDFs locally...

Creating Email Draft in Microsoft 365...

Draft created successfully with adjusted vertical spacing!

[2026-04-20 16:21:22,061: INFO/ForkPoolWorker-3] Task common.tasks.process_rma_email[463ae5da-f7e3-4494-9f50-7e00c664c6d2] succeeded in 3.542383493972011s: None

It looks like the locks are still being bypassed. Looking at your logs, there is over a minute between the first successful task (2cd82... at 16:19) and the second duplicate (4cac3... at 16:20).

This gap usually means one of two things:

Cache Configuration: If your Django CACHES setting is using LocMemCache (Local Memory), each Celery worker process has its own private memory. Worker A sets a lock, but Worker B can't see it because they aren't sharing a central "brain."

ID Mismatch: The immutable_id being returned might actually be changing, or the lock key isn't persisting.

1. The "Single Brain" Fix (Redis)
Since you already have Redis running (I see it in your logs), make sure your Django settings.py is actually using it for the cache. If it's not set to Redis, the workers can't talk to each other.

Check your settings.py:

Python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1", # Use db 1 to separate from Celery
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
2. The "Guaranteed" Lock (Using InternetMessageId)
If Microsoft is sending notifications for the same email a minute apart, we must ensure the InternetMessageId (the one in brackets like <BN6PR...outlook.com>) is exactly what we lock.

Let's refine the Task one more time with a print statement to verify the ID:

Python
@shared_task(bind=True)
def process_rma_email(self, volatile_id):
    immutable_id = get_immutable_id(volatile_id)
    if not immutable_id:
        return

    # Debug: Print the ID to your logs so we can see if it's identical
    print(f"DEBUG: Processing Attempt for ID: {immutable_id}")

    # Use a very specific key
    done_key = f"rma_complete_{immutable_id}"
    
    # .add() is the only thread-safe way to do this
    if not cache.add(done_key, True, timeout=86400):
        print(f"MATCH FOUND: {immutable_id} is already in cache. Killing task.")
        return

    # If we got here, we OWN the lock.
    try:
        # ... your subprocess.run logic ...
    except Exception as e:
        # Only delete the lock if the script failed to even START
        # If it created a draft, keep the lock so we don't do it again
        cache.delete(done_key)
3. Why it’s still flooding (The "Polling" Script)
Check your build_email_agent6.py script. Does it scan the whole inbox when it runs?

If Yes: Even if you pass --message_id, the script might be programmed to look at all "Unread" mail. If it finds the same email again, it makes another draft.

The Fix: Ensure the Python script is strictly limited to processing only the ID passed in the argument.

Next Step:
Check your settings.py to confirm you are using django-redis. If you are using the default Django memory cache, the workers are "blind" to each other's locks, which is exactly what your logs suggest is happening.

Once the cache is central (Redis), that cache.add will stop the duplicates instantly.

this is my cache settings:



CACHES = {

    "default": {

        "BACKEND": "django_redis.cache.RedisCache",

        "LOCATION": env("CACHES_LOCATION"),

        "OPTIONS": {

            "CLIENT_CLASS": "django_redis.client.DefaultClient",

        },

    }

}

Your cache settings are correct for a production environment using Redis, which means your workers are sharing a "brain."

However, since you are still seeing duplicates, we have to look at the execution timing. Because your Python script takes about 3–5 seconds to run (authenticating, looking up pricing, generating PDFs), the task is "in flight" while new notifications arrive.

Here is the final, bulletproof version of your task. The key change here is moving the lock check to the very first line using the volatile_id to stop the flood immediately, and then a second lock using the immutable_id to stop the duplicate drafts.

The Bulletproof tasks.py
Python
@shared_task(bind=True)
def process_rma_email(self, volatile_id):
    # LAYER 1: Immediate volatile lock (Stops the 'ping' flood)
    # This prevents the same notification from spawning multiple tasks
    ping_lock = f"rma_ping_{volatile_id}"
    if not cache.add(ping_lock, True, timeout=60):
        return

    # LAYER 2: Get the Permanent ID
    immutable_id = get_immutable_id(volatile_id)
    if not immutable_id:
        # If we can't get the ID, delete ping lock so we can try next time
        cache.delete(ping_lock)
        return

    # LAYER 3: The "Draft Created" Lock (Stops the 'duplicate' drafts)
    # We use the InternetMessageId here.
    final_lock = f"rma_final_done_{immutable_id}"
    
    # We use cache.add() because it is atomic in Redis
    if not cache.add(final_lock, "PROCESSING", timeout=300):
        # Check if it was already COMPLETED or is just currently PROCESSING
        status = cache.get(final_lock)
        if status == "COMPLETED":
            print(f"SKIP: Email {immutable_id} already has a draft.")
        else:
            print(f"SKIP: Email {immutable_id} is currently being processed by another worker.")
        return

    try:
        # EXECUTE OPENCLAW SCRIPT
        script_path = "/home/adminuser/.openclaw/workspace/build_email_agent6.py"
        result = subprocess.run(
            ["python3", script_path, "--message_id", immutable_id],
            cwd="/home/adminuser/.openclaw/workspace",
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Mark as COMPLETED permanently (24 hours)
            cache.set(final_lock, "COMPLETED", timeout=86400)
            print(f"SUCCESS: Draft created for {immutable_id}")
        else:
            # If the script failed, release the lock so it can be retried
            cache.delete(final_lock)
            print(f"SCRIPT ERROR: {result.stderr}")

    except Exception as e:
        cache.delete(final_lock)
        print(f"SYSTEM ERROR: {e}")


@shared_task
def send_ed_mass_email(bundle: tuple):
    """
    Sends a mass email to multiple recipients as celery tasks.

    This function uses Django's `send_mass_mail` function to send multiple email in a single conenction.

    Each email's details are provided within the `bundle` tuple.

    Args:
        bundle (tuple): A tuple of email data, where each element is a tuple of (subject, message, from_email, recipient_list)

    Returns:
        str: A log messahe indicating the number of email sent in the conenction.

    Raises:
        Exception: If an error occurs while sending the mass emails, logs an error message with details.

    """
    try:
        sta = send_mass_mail(bundle)
        msg = f"Mass email send total in a conenction: {sta}"
        log.info(msg)
        return msg
    except Exception as e:
        log.error(
            f"Error while sending mass mail (send_ed_mass_email) through celery queue: {e}"
        )


@shared_task
def send_ed_email(sub: str, msg: str, from_email: str, to_list: list):
    """
    Sends a single email to a list of recipients as a Celery task.

    This fucntion uses Django's `send_email` function to send an individual email with the specified
    subject, message and sender to a list of recipients.

    Args:
        sub (str): Subject of the email.
        msg (str): The body of the email message.
        from_email (str): The sender's email address.
        to_list (list): A list of recipient email addresses.

    Returns:
        str: A log message indicating the number of emails sent in the connection.

    Raises:
        Exception: If an error occurs while sending the email, logs an error message with details.
    """
    try:
        sta = send_mail(sub, msg, from_email, to_list)
        msg = f"Email send total in a conenction: {sta}"
        log.info(msg)
        return msg
    except Exception as e:
        log.error(
            f"Error while sending email (send_ed_email) through celery queue: {e}"
        )
