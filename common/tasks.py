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


@shared_task(bind=True, max_retries=3)
def process_rma_email(self, volatile_id):
    # 1. Get the permanent ID (InternetMessageId)
    immutable_id = get_immutable_id(volatile_id)

    if not immutable_id:
        print(
            f"Could not resolve ID for {volatile_id}. It might be deleted or delayed."
        )
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
            check=True,
        )
    except subprocess.CalledProcessError as e:
        # If the script fails, remove the lock so we can retry later
        cache.delete(processing_key)
        print(f"Script failed: {e}")


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
