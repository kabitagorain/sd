from django.contrib import admin
from django.core.cache import cache
from common.utils import SdMailService
from .models import *


class RmaRequestsAdmin(admin.ModelAdmin):
    """
    Admin configuration for the RmaRequests model.

    This class customizes the admin interface for the RmaRequests model,
    providing various display, filtering, and ordering options.
    """

    list_display = (
        "rma_number",
        "customer_name",
        "email",
        "order_ref",
        "product_sku",
        "rma_instructions",
        "status",
    )
    list_filter = ("status",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    search_fields = ["rma_number", "order_ref", "product_sku", "email"]
    search_help_text = "Search by rma_number or order_ref or product_sku or email"
    list_per_page = 20
    readonly_fields = [
        "rma_number",
        "customer_name",
        "email",
        "order_ref",
        "product_sku",
        "phone",
        "reason_for_return",
    ]

    def save_model(self, request, obj, form, change):
        """
        Override the save_model method to send an email when the RMA status changes.

        This method checks if the RMA status is 'rma_sent' and sends an email
        to the customer with the RMA instructions.

        Args:
            request (HttpRequest): The HTTP request object.
            obj (RmaRequests): The RMA request object being saved.
            form (ModelForm): The form used to edit the object.
            change (bool): True if the object is being changed, False if it is being created.
        """

        mail_service = SdMailService()
        if change:
            rma_id = obj.id
            # Cache the RMA request to reduce database hits.
            cache.set(f"rma_{rma_id}", obj, timeout=900)
            if obj.status == "rma_sent":
                mail_service.send_rma_instruction_to_customer(rma_id)

        super().save_model(request, obj, form, change)


admin.site.register(RmaRequests, RmaRequestsAdmin)
