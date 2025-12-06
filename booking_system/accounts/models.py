"""
User account models.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import TimeStampedModel


class User(AbstractUser):
    """Custom user model extending Django's AbstractUser."""
    ROLE_ADMIN = 'admin'
    ROLE_STAFF = 'staff'
    ROLE_CUSTOMER = 'customer'
    
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_STAFF, 'Staff'),
        (ROLE_CUSTOMER, 'Customer'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_CUSTOMER
    )
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        """Check if user is admin."""
        return self.role == self.ROLE_ADMIN or self.is_superuser

    @property
    def is_staff_member(self):
        """Check if user is staff."""
        return self.role == self.ROLE_STAFF

    @property
    def is_customer_user(self):
        """Check if user is customer."""
        return self.role == self.ROLE_CUSTOMER
