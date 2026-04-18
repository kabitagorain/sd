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
