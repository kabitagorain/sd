from django.contrib import admin
from account.models import User

admin.site.register(User)

"""
Registers the User model with the Django admin interface.

This allows the User model to be managed through the Django admin site.
"""
