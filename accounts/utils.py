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
        # Check if staff profile exists, if not redirect to completion
        try:
            from staff.models import Staff
            Staff.objects.get(user=user)
            return 'staff:staff_dashboard'
        except Staff.DoesNotExist:
            return 'staff:staff_complete_profile'
    elif user.role == 'customer':
        return 'customers:customer_dashboard'
    else:
        return 'customers:customer_dashboard'  # Default to customer dashboard

