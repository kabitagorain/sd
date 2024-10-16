
import random
import string
from rma.models import RmaRequests


def generate_rma_number():
    # get the last RMA number from the database and increment it
    last_rma = RmaRequests.objects.order_by('id').last()
    if last_rma:
        # Extract the numeric part from the previous rma
        last_number = int(last_rma.rma_number.split('-')[-1])
        new_number = last_number + 1
    else:
        new_number = 1
        
    # # generate a random number string of a 3 character
    # random_str = ''.join(random.choice(string.ascii_uppercase + string.digits, k=3))
    
    # formate the new RMA number with a prefix and zero padding
    return f'RMA-{new_number:05d}'