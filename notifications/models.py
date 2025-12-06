"""
Notification models.
"""
from django.db import models
from core.models import TimeStampedModel


class Notification(TimeStampedModel):
    """Notification template model."""
    TYPE_EMAIL = 'email'
    TYPE_SMS = 'sms'
    TYPE_CHOICES = [
        (TYPE_EMAIL, 'Email'),
        (TYPE_SMS, 'SMS'),
    ]

    EVENT_NEW = 'new'
    EVENT_APPROVED = 'approved'
    EVENT_CANCELLED = 'cancelled'
    EVENT_REJECTED = 'rejected'
    EVENT_REMINDER = 'reminder'
    EVENT_FOLLOW_UP = 'follow_up'
    
    EVENT_CHOICES = [
        (EVENT_NEW, 'New Appointment'),
        (EVENT_APPROVED, 'Appointment Approved'),
        (EVENT_CANCELLED, 'Appointment Cancelled'),
        (EVENT_REJECTED, 'Appointment Rejected'),
        (EVENT_REMINDER, 'Reminder'),
        (EVENT_FOLLOW_UP, 'Follow-up'),
    ]

    SEND_TO_CUSTOMER = 'customer'
    SEND_TO_STAFF = 'staff'
    SEND_TO_ADMIN = 'admin'
    
    SEND_TO_CHOICES = [
        (SEND_TO_CUSTOMER, 'Customer'),
        (SEND_TO_STAFF, 'Staff'),
        (SEND_TO_ADMIN, 'Admin'),
    ]

    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES)
    send_to = models.CharField(max_length=20, choices=SEND_TO_CHOICES)
    active = models.BooleanField(default=True)
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField(help_text="Message template with placeholders")
    reminder_hours_before = models.IntegerField(
        null=True,
        blank=True,
        help_text="Hours before appointment to send reminder (for reminder type)"
    )

    class Meta:
        ordering = ['event_type', 'type', 'send_to']
        unique_together = ['type', 'event_type', 'send_to']

    def __str__(self):
        return f"{self.get_type_display()} - {self.get_event_type_display()} - {self.get_send_to_display()}"


class SentNotification(TimeStampedModel):
    """Record of sent notifications."""
    STATUS_SENT = 'sent'
    STATUS_FAILED = 'failed'
    STATUS_PENDING = 'pending'
    
    STATUS_CHOICES = [
        (STATUS_SENT, 'Sent'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_PENDING, 'Pending'),
    ]

    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='sent_notifications'
    )
    customer_appointment = models.ForeignKey(
        'appointments.CustomerAppointment',
        on_delete=models.CASCADE,
        related_name='sent_notifications'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    recipient = models.CharField(
        max_length=255,
        help_text="Email or phone number"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'sent_at']),
        ]

    def __str__(self):
        return f"{self.notification} - {self.recipient} - {self.get_status_display()}"
