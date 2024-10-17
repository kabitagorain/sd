from django import forms
from .models import RmaRequests
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha import widgets


class RmaForm(forms.ModelForm):
    """
    Form for submitting RMA requests.

    This form handles the validation and submission of RMA requests from
    customers, including fields for customer information and return reasons.
    """

    captcha = ReCaptchaField(
        widget=widgets.ReCaptchaV2Checkbox(
            api_params={"hl": "cl", "onload": "onLoadFunc"}
        ),
        label="",
    )

    class Meta:
        model = RmaRequests
        fields = [
            "customer_name",
            "email",
            "phone",
            "order_ref",
            "product_sku",
            "reason_for_return",
        ]

        widgets = {
            "customer_name": forms.TextInput(
                attrs={
                    "placeholder": "Customer name included with the order",
                    "class": "form-control",
                    "aria-label": "name",
                    "autocomplete": "name",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "Email address included with the order",
                    "class": "form-control",
                    "aria-label": "email",
                    "autocomplete": "email",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "placeholder": "Phone number included with the order",
                    "class": "form-control",
                    "aria-label": "phone",
                    "autocomplete": "phone",
                }
            ),
            "order_ref": forms.TextInput(
                attrs={
                    "placeholder": "Order reference number",
                    "class": "form-control",
                    "aria-label": "order-ref",
                    "autocomplete": "order-ref",
                }
            ),
            "product_sku": forms.TextInput(
                attrs={
                    "placeholder": "Product SKU",
                    "class": "form-control",
                    "aria-label": "sku",
                    "autocomplete": "sku",
                }
            ),
            "reason_for_return": forms.Textarea(
                attrs={
                    "placeholder": "Reason for return",
                    "class": "form-control",
                    "aria-label": "reason_for_return",
                    "autocomplete": "reason-for-return",
                }
            ),
        }

        labels = {
            "customer_name": "Customer Name",
            "email": "Order Email",
            "phone": "Order Phone Number",
            "order_ref": "Odrer Reference",
            "product_sku": "Product SKU",
            "reason_for_return": "Reason for return",
        }

    def __init__(self, *args, **kwargs):
        """
        Initialize the form with custom configurations.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super(RmaForm, self).__init__(*args, **kwargs)
        # Removing colone(:) suffix
        self.label_suffix = ""

    def clean(self):
        """
        Validate the form data to prevent duplicate RMA requests.

        This method ensures that no RMA request exists with the same
        email, order reference, and product SKU combination.

        Returns:
            dict: The cleaned data.

        Raises:
            ValidationError: If an RMA request with the same details already exists.
        """
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        order_ref = cleaned_data.get("order_ref")
        product_sku = cleaned_data.get("product_sku")

        if RmaRequests.objects.filter(
            email=email, order_ref=order_ref, product_sku=product_sku
        ).exists():
            raise forms.ValidationError(
                "An RMA request already exists for this product SKU with the same email and order reference."
            )

        return cleaned_data
