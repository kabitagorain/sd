from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom User model that extends Django's built-in AbstractUser.

    This model is currently identical to the default AbstractUser, but is set up
    for future extension, allowing additional fields or custom behavior to be added.

    Attributes inherited from AbstractUser:
        username (str): Required. 150 characters or fewer. Letters, digits, and @/./+/-/_ only.
        first_name (str): Optional. 150 characters or fewer.
        last_name (str): Optional. 150 characters or fewer.
        email (str): Optional. Email address of the user.
        password (str): Required. User password.
        is_staff (bool): Optional. Designates whether the user can log into the admin site.
        is_active (bool): Optional. Designates whether this user should be treated as active.
        date_joined (datetime): Optional. The date and time when the user account was created.
    """

    pass
