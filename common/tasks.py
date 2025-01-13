from celery import shared_task
from django.core.mail import send_mail, send_mass_mail
import logging

log = logging.getLogger("log")


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
        log.error(f"Error while sending email (send_ed_email) through celery queue: {e}")
