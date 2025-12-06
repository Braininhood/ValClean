"""
Appointment models.
"""
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from core.models import TimeStampedModel
import secrets


class Series(TimeStampedModel):
    """Recurring appointment series."""
    REPEAT_TYPE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    repeat_type = models.CharField(max_length=20, choices=REPEAT_TYPE_CHOICES)
    repeat_interval = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Repeat every X days/weeks/months"
    )
    until_date = models.DateField(null=True, blank=True)
    occurrences = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of occurrences (alternative to until_date)"
    )

    def __str__(self):
        return f"Series {self.id} - {self.get_repeat_type_display()}"


class Appointment(TimeStampedModel):
    """Appointment model."""
    staff = models.ForeignKey(
        'staff.Staff',
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    series = models.ForeignKey(
        Series,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments'
    )
    calendar_event_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="Event ID from calendar provider (Google/Outlook/Apple)"
    )
    calendar_provider = models.CharField(
        max_length=20,
        choices=[
            ('none', 'None'),
            ('google', 'Google'),
            ('outlook', 'Outlook'),
            ('apple', 'Apple'),
        ],
        default='none'
    )
    internal_note = models.TextField(
        blank=True,
        help_text="Internal notes (not visible to customers)"
    )
    extras_duration = models.IntegerField(
        default=0,
        help_text="Additional duration from extras in minutes"
    )

    class Meta:
        ordering = ['start_date']
        indexes = [
            models.Index(fields=['staff', 'start_date']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return f"{self.service.title} - {self.staff.full_name} - {self.start_date}"

    @property
    def duration(self):
        """Calculate appointment duration in minutes."""
        delta = self.end_date - self.start_date
        return int(delta.total_seconds() / 60)


class CustomerAppointment(TimeStampedModel):
    """Link between customer and appointment."""
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_CANCELLED = 'cancelled'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.CASCADE,
        related_name='customer_appointments'
    )
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='customer_appointments'
    )
    payment = models.ForeignKey(
        'payments.Payment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customer_appointments'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    number_of_persons = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    extras = models.JSONField(
        default=list,
        blank=True,
        help_text="Selected service extras"
    )
    custom_fields = models.JSONField(
        default=list,
        blank=True,
        help_text="Custom field values"
    )
    token = models.CharField(
        max_length=64,
        unique=True,
        blank=True,
        help_text="Unique token for cancellation/approval links"
    )
    time_zone_offset = models.IntegerField(
        default=0,
        help_text="Client timezone offset in minutes"
    )
    # location = models.ForeignKey(
    #     'services.Location',
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name='appointments'
    # )
    # TODO: Add Location model when implementing multi-location support
    compound_token = models.CharField(
        max_length=64,
        blank=True,
        help_text="Token for multi-appointment bookings"
    )
    compound_service = models.ForeignKey(
        'services.Service',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='compound_appointments'
    )

    class Meta:
        ordering = ['appointment__start_date']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['token']),
            models.Index(fields=['compound_token']),
        ]

    def __str__(self):
        return f"{self.customer.name} - {self.appointment}"

    def save(self, *args, **kwargs):
        """Generate token if not set."""
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    def cancel(self):
        """Cancel this appointment."""
        self.status = self.STATUS_CANCELLED
        self.save()
