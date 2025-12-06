"""
Django signals for automatic calendar sync on appointment changes.
"""
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from appointments.models import Appointment, CustomerAppointment
from .services import get_calendar_service
import logging

logger = logging.getLogger(__name__)


def get_request_from_signal():
    """Try to get request object from thread local storage."""
    try:
        from django.contrib.auth.middleware import get_user
        from threading import local
        # This is a workaround - in production, you might want to pass request explicitly
        # For now, we'll build URLs without request context
        return None
    except:
        return None


@receiver(post_save, sender=Appointment)
def sync_appointment_to_calendar(sender, instance, created, **kwargs):
    """
    Sync appointment to calendar when created or updated.
    """
    staff = instance.staff
    
    if staff.calendar_provider == 'none':
        return
    
    calendar_service = get_calendar_service(staff)
    if not calendar_service:
        return
    
    # Get customer appointment for event details
    customer_appointment = instance.customer_appointments.first()
    
    # Try to get request from thread local (may not always be available)
    request = get_request_from_signal()
    
    try:
        if created:
            # Create new calendar event
            result = calendar_service.create_event(instance, customer_appointment, request)
            if result.get('success'):
                instance.calendar_event_id = result.get('event_id', '')
                instance.calendar_provider = staff.calendar_provider
                # Save without triggering signal again
                Appointment.objects.filter(id=instance.id).update(
                    calendar_event_id=result.get('event_id', ''),
                    calendar_provider=staff.calendar_provider
                )
            else:
                logger.warning(f"Calendar sync failed for appointment {instance.id}: {result.get('error')}")
        else:
            # Update existing calendar event
            if instance.calendar_event_id:
                result = calendar_service.update_event(instance, instance.calendar_event_id, customer_appointment, request)
                if not result.get('success'):
                    logger.warning(f"Calendar update failed for appointment {instance.id}: {result.get('error')}")
            else:
                # Event ID missing, try to create
                result = calendar_service.create_event(instance, customer_appointment, request)
                if result.get('success'):
                    Appointment.objects.filter(id=instance.id).update(
                        calendar_event_id=result.get('event_id', ''),
                        calendar_provider=staff.calendar_provider
                    )
    except Exception as e:
        logger.error(f"Error syncing appointment {instance.id} to calendar: {str(e)}")


@receiver(pre_delete, sender=Appointment)
def delete_appointment_from_calendar(sender, instance, **kwargs):
    """
    Delete appointment from calendar when appointment is deleted.
    """
    if not instance.calendar_event_id or instance.calendar_provider == 'none':
        return
    
    staff = instance.staff
    calendar_service = get_calendar_service(staff)
    
    if not calendar_service:
        return
    
    try:
        result = calendar_service.delete_event(instance.calendar_event_id)
        if not result.get('success'):
            logger.warning(f"Calendar delete failed for appointment {instance.id}: {result.get('error')}")
    except Exception as e:
        logger.error(f"Error deleting appointment {instance.id} from calendar: {str(e)}")

