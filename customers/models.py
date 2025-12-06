"""
Customer models.
"""
from django.db import models
from django.contrib.auth import get_user_model
from core.models import BaseModel, TimeStampedModel

User = get_user_model()


class Customer(TimeStampedModel):
    """Customer model."""
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customer_profile'
    )
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    
    # Address fields
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    county = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='UK')
    address_validated = models.BooleanField(
        default=False,
        help_text="True if address was validated using AddressNow"
    )
    
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
        ]

    def __str__(self):
        return self.name

    @property
    def full_address(self):
        """Return formatted full address."""
        parts = [
            self.address_line1,
            self.address_line2,
            self.city,
            self.county,
            self.postcode,
            self.country
        ]
        return ", ".join(filter(None, parts))
