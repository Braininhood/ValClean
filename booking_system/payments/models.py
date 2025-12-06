"""
Payment models.
"""
from django.db import models
from django.core.validators import MinValueValidator
from core.models import TimeStampedModel


class Payment(TimeStampedModel):
    """Payment model."""
    TYPE_LOCAL = 'local'
    TYPE_PAYPAL = 'paypal'
    TYPE_STRIPE = 'stripe'
    TYPE_AUTHORIZENET = 'authorize_net'
    TYPE_2CHECKOUT = '2checkout'
    TYPE_PAYULATAM = 'payu_latam'
    TYPE_PAYSON = 'payson'
    TYPE_MOLLIE = 'mollie'
    TYPE_COUPON = 'coupon'
    TYPE_WOOCOMMERCE = 'woocommerce'
    
    TYPE_CHOICES = [
        (TYPE_LOCAL, 'Local Payment'),
        (TYPE_PAYPAL, 'PayPal'),
        (TYPE_STRIPE, 'Stripe'),
        (TYPE_AUTHORIZENET, 'Authorize.Net'),
        (TYPE_2CHECKOUT, '2Checkout'),
        (TYPE_PAYULATAM, 'PayU Latam'),
        (TYPE_PAYSON, 'Payson'),
        (TYPE_MOLLIE, 'Mollie'),
        (TYPE_COUPON, 'Coupon (100% discount)'),
        (TYPE_WOOCOMMERCE, 'WooCommerce'),
    ]

    STATUS_COMPLETED = 'completed'
    STATUS_PENDING = 'pending'
    STATUS_FAILED = 'failed'
    STATUS_REFUNDED = 'refunded'
    
    STATUS_CHOICES = [
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_PENDING, 'Pending'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_REFUNDED, 'Refunded'),
    ]

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Payment details (items, customer info, etc.)"
    )
    transaction_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="Transaction ID from payment gateway"
    )
    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'type']),
            models.Index(fields=['transaction_id']),
        ]

    def __str__(self):
        return f"{self.get_type_display()} - {self.total} - {self.get_status_display()}"

    @property
    def is_paid(self):
        """Check if payment is completed."""
        return self.status == self.STATUS_COMPLETED

    @property
    def remaining_amount(self):
        """Calculate remaining amount to be paid."""
        return max(self.total - self.paid, 0)
