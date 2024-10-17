from django.shortcuts import render
from common.context_processor import site_info
from common.utils import SdMailService
from rma.forms import RmaForm
from rma.utils import generate_rma_number
from django.core.cache import cache

EMAIL_SERVICE = SdMailService()


def rma_request_view(request):
    """
    Handle the RMA request form submission.

    This view renders the RMA request form, validates submitted data,
    generates an RMA number, and sends an email notification upon successful
    form submission.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered RMA request form or success message.
    """
    form = RmaForm()
    site_data = site_info()

    # Editing site meta title and description
    site_data["title"] = "RMA request"
    site_data["description"] = "Effortless manage your return with our RMA System!"

    context = {"form": form, "site_data": site_data}

    if request.method == "POST":
        post_form = RmaForm(request.POST)
        if post_form.is_valid():

            rma_request = post_form.save(commit=False)
            rma_request.rma_number = generate_rma_number()
            rma_request.save()

            rma_id = rma_request.id

            # To reduce database hit, it will delete inside send_rma_genaration_email function
            cache.set(f"rma_{rma_id}", rma_request, timeout=900)

            EMAIL_SERVICE.send_rma_genaration_email(rma_id)

            context["rma_number"] = rma_request.rma_number
            response = render(
                request, "rma/rma_form_block_with_success_message.html", context=context
            )
            response["X-Robots-Tag"] = "noindex, nofollow"
            return response
        else:
            context["form"] = post_form
            response = render(request, "rma/rma_form_block.html", context=context)
            response["X-Robots-Tag"] = "noindex, nofollow"
            return response
    else:
        response = render(request, "rma/rma_request.html", context=context)
        response["X-Robots-Tag"] = "noindex, nofollow"
        return response
