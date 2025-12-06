"""
Coupon models.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from core.models import TimeStampedModel


class Coupon(TimeStampedModel):
    """Coupon/Discount code model."""
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Coupon code (case-insensitive)"
    )
    discount = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Discount percentage (0-100)"
    )
    deduction = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Fixed amount deduction"
    )
    usage_limit = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Maximum number of times coupon can be used"
    )
    used = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    start_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Coupon validity start date"
    )
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Coupon validity end date"
    )
    services = models.ManyToManyField(
        'services.Service',
        blank=True,
        related_name='coupons',
        help_text="Services this coupon applies to (empty = all services)"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
        ]

    def __str__(self):
        return f"{self.code} - {self.discount}%"

    def is_valid(self, service_ids=None):
        """Check if coupon is valid for given services."""
        # Check usage limit
        if self.used >= self.usage_limit:
            return False

        # Check date validity
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False

        # Check service restrictions
        if self.services.exists():
            if not service_ids:
                return False
            coupon_service_ids = set(self.services.values_list('id', flat=True))
            if not set(service_ids).intersection(coupon_service_ids):
                return False

        return True

    def apply(self, amount):
        """Apply coupon to amount and return discounted amount."""
        # Apply percentage discount
        discounted = amount * (100 - self.discount) / 100
        # Apply fixed deduction
        final_amount = discounted - self.deduction
        return max(final_amount, 0)

    def claim(self, quantity=1):
        """Mark coupon as used."""
        self.used += quantity
        self.save(update_fields=['used'])
