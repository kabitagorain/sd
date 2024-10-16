from django.db import models
from django.conf import settings

# Create your models here.
class RmaRequests(models.Model):
    '''
    = Customer will submit RMA request
    = Admin will check RM Request
    = Will approved from admin and email will sent autometically
    '''
    RMA_STATUS = settings.RMA_STATUS
    
    customer_name = models.CharField(max_length=120, help_text='Enter customer name matched with order')
    email = models.EmailField(help_text="Email that order generated for", db_index=True)
    phone = models.CharField(max_length=20, blank=True, help_text='Enter your phone number, it is optional.')
    order_ref = models.CharField(max_length=155, help_text="Enter order reference number, it is mandatory.", db_index=True)
    product_sku = models.CharField(help_text="Product SKU", max_length=150)
    reason_for_return = models.TextField(help_text="Why you want to return the product")
    rma_number = models.CharField(max_length=20, unique=True, blank=True, help_text="A Unique RMA will be generated, and will send through email!", editable=False, db_index=True)
    rma_instructions = models.TextField(
        blank=True, 
        help_text=
        "Instruction that customer will receive throguh email!\n"
        "What you will write here will use as a middle part of mail message.\n" 
        "Please edit default value added.\n"
        "Please ensure that there '$rma_number' variable as it is, and add in the appropiate place, which will replace by RMA number of this product. It is crutial!",
        default=        
        "1. Carefully pack the item in its original packaging, including all accessories and documentation.\n"
        "2. Clearly mark the RMA number '$rma_number' on the outside of the package.\n"
        "3. Ship the package to the following address.\n"  
        "4. Once the return is processed, we will notify you of the status and any further steps, if necessary.\n"
    )    
    status = models.CharField(max_length=50, default='pending', choices=RMA_STATUS, help_text="RMA status", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"RMA for orde {self.order_ref} - Status {self.status} - Order Email {self.email}"
