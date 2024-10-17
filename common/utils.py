from django.core.mail import send_mail, send_mass_mail
from django.core.cache import cache
from common.context_processor import site_info
from ed import settings
from django.template.loader import render_to_string

import logging

log = logging.getLogger("log")


class SdMailService:
    """
    Service for sending emails related to RMA (Return Merchandise Authorization).

    This service handles sending emails for RMA requests and instructions,
    leveraging Django's email utilities and caching mechanisms.
    """

    def __init__(self):
        """
        Initializes the SdMailService, retrieving the site metadata.
        """
        self.site = site_info()

    def send_rma_genaration_email(self, rma_id):
        """
        Sends RMA generation emails to the admin and customer.

        Uses `send_mass_mail` to send multiple emails in one connection.
        Emails are sent to all addresses configured in the .env file,
        as well as the customer who created the RMA request.
        also delete cache as soon as operation done which is set in the used place.

        Args:
            rma_id (int): The ID of the RMA request.
        """
        rma = cache.get(f"rma_{rma_id}")

        recepients = {"admin": settings.ADMIN, "customer": [rma.email]}

        context = {
            "rma_number": rma.rma_number,
            "customer_name": rma.customer_name,
            "customer_email": rma.email,
            "customer_phone": rma.phone,
            "product_sku": rma.product_sku,
            "reason_for_return": rma.reason_for_return,
            "submitted_date": rma.created_at,
            "site_name": self.site.get("name"),
        }

        admin_msg = render_to_string("emails/rma_request_admin_msg.txt", context)
        customer_msg = render_to_string(
            "emails/rma_genaration_customer_msg.txt", context
        )

        email_bundle = []

        try:
            for key, email_list in recepients.items():
                if key == "admin":
                    email_bundle.append(
                        (
                            f"[{self.site.get('name')}] New RMA Submitted for Product SKU #{rma.product_sku}",
                            admin_msg,
                            settings.DEFAULT_FROM_EMAIL,
                            email_list,
                        )
                    ),
                elif key == "customer":
                    email_bundle.append(
                        (
                            f"[{self.site.get('name')}] We Have Received Your RMA for Product SKU #{rma.product_sku}",
                            customer_msg,
                            settings.DEFAULT_FROM_EMAIL,
                            email_list,
                        )
                    ),

            send_mass_mail(tuple(email_bundle))
        except Exception as e:
            log.error(f"Error duing sending send_rma_genaration_email: {e}")
        cache.delete(f"rma_{rma_id}")

    def sent_rma_instruction_to_customer(self, rma_id):
        """
        Sends RMA instructions to the customer when the RMA status is updated with the status `rma_sent` from the admin interface.

        Uses `send_mail` to send a single email to the customer with instructions.

        also delete cache as soon as operation done which is set in the used place.

        Args:
            rma_id (int): The ID of the RMA request.
        """
        rma = cache.get(f"rma_{rma_id}")

        context = {
            "rma_number": rma.rma_number,
            "customer_name": rma.customer_name,
            "customer_email": rma.email,
            "customer_phone": rma.phone,
            "product_sku": rma.product_sku,
            "reason_for_return": rma.reason_for_return,
            "submitted_date": rma.created_at,
            "site_name": self.site.get("name"),
            "return_address": self.site.get("return_address"),
            "admin_instruction": (rma.rma_instructions).replace(
                "$rma_number", rma.rma_number
            ),
        }
        rma_instruction_msg = render_to_string(
            "emails/rma_instruction_msg.txt", context
        )
        try:
            send_mail(
                f"[{self.site.get('name')}] Instruction to Return Product with SKU #{rma.product_sku} for RMA {rma.rma_number}",
                rma_instruction_msg,
                settings.DEFAULT_FROM_EMAIL,
                [rma.email],
            )
        except Exception as e:
            log.error(f"Error duing sending send_rma_genaration_email: {e}")
        cache.delete(f"rma_{rma_id}")
