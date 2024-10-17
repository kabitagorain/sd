from django.db import models
from django.conf import settings


# Create your models here.
class RmaRequests(models.Model):
    """
    Model representing an RMA (Return Merchandise Authorization) request.

    This model is used to handle the submission and management of RMA requests
    from customers, including tracking the request's status, associated customer
    details, and instructions for return processing. The admin can approve the request,
    and email notifications will be sent to the customer
    based on the status.

    Attributes:
        RMA_STATUS (list): List of status choices for the RMA request, defined in settings.

        customer_name (str): The name of the customer as it appears on the order.
            This field has a maximum length of 120 characters.

        email (str): The email address associated with the order. Indexed for optimized lookups.

        phone (str): An optional phone number provided by the customer.
            This field has a maximum length of 20 characters.

        order_ref (str): The order reference number associated with the RMA request.
            This field is required and indexed for optimized lookups. It has a maximum length of 155 characters.

        product_sku (str): The SKU (Stock Keeping Unit) of the product being returned.
            This field has a maximum length of 150 characters.

        reason_for_return (str): The reason provided by the customer for returning the product.

        rma_number (str): A unique identifier for the RMA request,
            automatically generated when the request is created. This field is indexed and has a maximum length of 20 characters.

        rma_instructions (str): Instructions provided to the customer for returning the product.
            These instructions will be sent in an email and can include a dynamic placeholder for the RMA number.

        status (str): The current status of the RMA request, with a default value of 'pending'.
            The available choices are defined in the settings.RMA_STATUS list.

        created_at (datetime): The date and time when the RMA request was created.
            Automatically set to the current date and time when the record is created.
    """

    RMA_STATUS = settings.RMA_STATUS

    customer_name = models.CharField(
        max_length=120, help_text="Enter customer name matched with order"
    )
    email = models.EmailField(help_text="Email that order generated for", db_index=True)
    phone = models.CharField(
        max_length=20, blank=True, help_text="Enter your phone number, it is optional."
    )
    order_ref = models.CharField(
        max_length=155,
        help_text="Enter order reference number, it is mandatory.",
        db_index=True,
    )
    product_sku = models.CharField(help_text="Product SKU", max_length=150)
    reason_for_return = models.TextField(help_text="Why you want to return the product")
    rma_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        help_text="A Unique RMA will be generated, and will send through email!",
        editable=False,
        db_index=True,
    )
    rma_instructions = models.TextField(
        blank=True,
        help_text="Instruction that customer will receive throguh email!\n"
        "What you will write here will use as a middle part of mail message.\n"
        "Please edit default value added.\n"
        "Please ensure that there '$rma_number' variable as it is, and add in the appropiate place, which will replace by RMA number of this product. It is crutial!",
        default="1. Carefully pack the item in its original packaging, including all accessories and documentation.\n"
        "2. Clearly mark the RMA number '$rma_number' on the outside of the package.\n"
        "3. Ship the package to the following address.\n"
        "4. Once the return is processed, we will notify you of the status and any further steps, if necessary.\n",
    )
    status = models.CharField(
        max_length=50,
        default="pending",
        choices=RMA_STATUS,
        help_text="RMA status",
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a string representation of the RMA request, including the order reference,
        status, and email address associated with the request.

        Returns:
            str: A formatted string representing the RMA request.
        """
        return f"RMA for orde {self.order_ref} - Status {self.status} - Order Email {self.email}"
