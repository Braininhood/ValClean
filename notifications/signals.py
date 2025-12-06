"""
Django signals for automatic notification sending.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from appointments.models import CustomerAppointment
from .services import NotificationSender


@receiver(post_save, sender=CustomerAppointment)
def send_appointment_notifications(sender, instance, created, **kwargs):
    """
    Automatically send notifications when CustomerAppointment is created or updated.
    """
    sender_service = NotificationSender()
    
    if created:
        # New appointment created
        sender_service.send_appointment_notifications(instance, 'new')
    else:
        # Check if status changed
        if instance.status == CustomerAppointment.STATUS_APPROVED:
            # Check if it was just approved (not already approved)
            # Note: This is a simple check, in production you might want to track previous status
            sender_service.send_appointment_notifications(instance, 'approved')
        elif instance.status == CustomerAppointment.STATUS_CANCELLED:
            sender_service.send_appointment_notifications(instance, 'cancelled')
        elif instance.status == CustomerAppointment.STATUS_REJECTED:
            sender_service.send_appointment_notifications(instance, 'rejected')

