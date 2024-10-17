
import random
import string
from rma.models import RmaRequests


def generate_rma_number():
    """
    Generate a unique RMA number.

    This function retrieves the last RMA request from the database, 
    increments the numeric portion, and formats the new RMA number with 
    a prefix.

    Returns:
        str: The newly generated RMA number.
    """
    last_rma = RmaRequests.objects.order_by('id').last()
    if last_rma:
        # Extract the numeric part from the previous RMA number.
        last_number = int(last_rma.rma_number.split('-')[-1])
        new_number = last_number + 1
    else:
        new_number = 1
        
    # Format the new RMA number with a prefix and zero padding.
    return f'RMA-{new_number:05d}'