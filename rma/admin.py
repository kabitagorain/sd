from django.contrib import admin
from django.core.cache import cache
from common.utils import SdMailService
from .models import *

# approve RMA by admin
# Sent RMA to the customer
# change status of the RMA

class RmaRequestsAdmin(admin.ModelAdmin):
    list_display = ('rma_number', 'customer_name', 'email', 'order_ref', 'product_sku', 'rma_instructions', 'status' ,)
    list_filter = ('status',)
    date_hierarchy = "created_at"
    ordering = ('-created_at',)
    search_fields = ["rma_number", 'order_ref','product_sku', 'email']
    search_help_text = "Search by rma_number or order_ref or product_sku or email"
    list_per_page = 20
    readonly_fields = ["rma_number", 'customer_name', 'email', 'order_ref', 'product_sku', 'phone', 'reason_for_return' ]
    
    def save_model(self, request, obj, form, change):
        """
        Overrides the save_model method to send an email
        when the object is changed.
        """
        mail_service = SdMailService()
        if change:  
            rma_id = obj.id
            # due to reduce databse hit this cach will be deleted inside sent_rma_instruction_to_customer function
            cache.set(f'rma_{rma_id}', obj, timeout=900) 
            if obj.status == 'rma_sent':
                mail_service.sent_rma_instruction_to_customer(rma_id)

   
        super().save_model(request, obj, form, change)

    

admin.site.register(RmaRequests, RmaRequestsAdmin)