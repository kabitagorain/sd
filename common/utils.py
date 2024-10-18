from django.core.mail import send_mail, send_mass_mail
from django.core.cache import cache
from common.context_processor import site_info
from ed import settings
from django.template.loader import render_to_string

import logging

log = logging.getLogger("log")


class SdMailService:
    """
    Service for handling email operations related to RMA (Return Merchandise Authorization).

    This service manages sending emails for RMA requests and instructions,
    using Django's email utilities and caching mechanisms.
    """

    def __init__(self):
        """
        Initializes the SdMailService instance.

        Retrieves site metadata, initializes the list of admin email addresses and from email.
        """
        self.site = site_info()
        self.admin_list = settings.ADMIN
        self.from_email = settings.DEFAULT_FROM_EMAIL

    def get_rma_from_cache(self, rma_id):
        """
        Retrieves an RMA request from the cache.

        Args:
            rma_id (int): The ID of the RMA request.

        Returns:
            RmaRequests: The RMA request object retrieved from the cache.
        """
        rma = cache.get(f"rma_{rma_id}")
        return rma

    def get_rma_email(self, rma_id):
        """
        Gets the email address associated with an RMA request.

        Args:
            rma_id (int): The ID of the RMA request.

        Returns:
            str: The email address associated with the RMA request.
        """
        return self.get_rma_from_cache(rma_id).email

    def get_rma_product_sku(self, rma_id):
        """
        Gets the product SKU associated with an RMA request.

        Args:
            rma_id (int): The ID of the RMA request.

        Returns:
            str: The product SKU associated with the RMA request.
        """
        return self.get_rma_from_cache(rma_id).product_sku

    def get_rma_rma_number(self, rma_id):
        """
        Gets the RMA number associated with an RMA request.

        Args:
            rma_id (int): The ID of the RMA request.

        Returns:
            str: The RMA number associated with the request.
        """
        return self.get_rma_from_cache(rma_id).rma_number

    def get_rma_admin_instruction(self, rma_id):
        """
        Retrieves the admin instructions for an RMA request.

        Args:
            rma_id (int): The ID of the RMA request.

        Returns:
            str: The admin instructions for the RMA, with the RMA number included.
        """
        rma = self.get_rma_from_cache(rma_id)
        return (rma.rma_instructions).replace("$rma_number", rma.rma_number)

    def get_context(self, rma_id):
        """
        Prepares the context data for an RMA email template.

        Args:
            rma_id (int): The ID of the RMA request.

        Returns:
            dict: The context dictionary containing RMA details and site information.
        """
        rma = self.get_rma_from_cache(rma_id)

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
        return context

    def send_rma_genaration_email(self, rma_id):
        """
        Sends RMA generation emails to the admin and the customer.

        Uses `send_mass_mail` to send multiple emails in one connection.
        Emails are sent to the addresses configured in the admin list, as well
        as the customer who created the RMA request. Once done, the cache is cleared.

        Args:
            rma_id (int): The ID of the RMA request.
        """
        recepients = {
            "admin": self.admin_list,
            "customer": [self.get_rma_email(rma_id)],
        }

        admin_msg = render_to_string(
            "emails/rma_request_admin_msg.txt", context=self.get_context(rma_id)
        )
        customer_msg = render_to_string(
            "emails/rma_genaration_customer_msg.txt", context=self.get_context(rma_id)
        )

        email_bundle = []

        try:
            for key, email_list in recepients.items():
                if key == "admin":
                    email_bundle.append(
                        (
                            f"[{self.site.get('name')}] New RMA Submitted for Product SKU #{self.get_rma_product_sku(rma_id)}",
                            admin_msg,
                            self.from_email,
                            email_list,
                        )
                    )
                elif key == "customer":
                    email_bundle.append(
                        (
                            f"[{self.site.get('name')}] We Have Received Your RMA for Product SKU #{self.get_rma_product_sku(rma_id)}",
                            customer_msg,
                            self.from_email,
                            email_list,
                        )
                    )

            send_mass_mail(tuple(email_bundle))
        except Exception as e:
            log.error(f"Error during sending send_rma_genaration_email: {e}")
        cache.delete(f"rma_{rma_id}")

    def send_rma_instruction_to_customer(self, rma_id):
        """
        Sends RMA instructions to the customer when the RMA status is updated.

        Uses `send_mail` to send a single email to the customer with instructions.
        The cache is cleared after the operation.

        Args:
            rma_id (int): The ID of the RMA request.
        """
        context = self.get_context(rma_id)
        context["admin_instruction"] = self.get_rma_admin_instruction(rma_id)

        rma_instruction_msg = render_to_string(
            "emails/rma_instruction_msg.txt", context
        )
        try:
            send_mail(
                f"[{self.site.get('name')}] Instruction to Return Product with SKU #{self.get_rma_product_sku(rma_id)} for RMA {self.get_rma_rma_number(rma_id)}",
                rma_instruction_msg,
                self.from_email,
                [self.get_rma_email(rma_id)],
            )
        except Exception as e:
            log.error(f"Error during sending RMA instructions email: {e}")
        cache.delete(f"rma_{rma_id}")
