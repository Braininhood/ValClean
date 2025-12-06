"""
Utility functions for accounts app.
"""
from django.contrib.auth import get_user_model

User = get_user_model()


def get_redirect_url_for_user(user):
    """Get appropriate redirect URL based on user role."""
    if user.is_superuser or user.role == 'admin':
        return 'admin:index'
    elif user.role == 'staff':
        return 'staff:staff_dashboard'
    elif user.role == 'customer':
        return 'customers:customer_dashboard'
    else:
        return 'customers:customer_dashboard'  # Default to customer dashboard

