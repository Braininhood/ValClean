"""
Celery tasks for notification system.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from appointments.models import CustomerAppointment
from .models import Notification
from .services import NotificationSender
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_appointment_reminders():
    """
    Celery task to send appointment reminders.
    Runs periodically to check for appointments that need reminders.
    """
    sender_service = NotificationSender()
    
    # Get all active reminder notifications
    reminder_notifications = Notification.objects.filter(
        event_type=Notification.EVENT_REMINDER,
        active=True
    )
    
    if not reminder_notifications.exists():
        logger.info("No active reminder notifications configured")
        return
    
    # Get upcoming appointments that need reminders
    now = timezone.now()
    sent_count = 0
    error_count = 0
    
    for notification in reminder_notifications:
        hours_before = notification.reminder_hours_before or 24
        
        # Calculate target time for reminders
        reminder_time_start = now + timedelta(hours=hours_before - 1)  # 1 hour window
        reminder_time_end = now + timedelta(hours=hours_before + 1)
        
        # Get appointments in the reminder window
        appointments = CustomerAppointment.objects.filter(
            appointment__start_date__gte=reminder_time_start,
            appointment__start_date__lte=reminder_time_end,
            status__in=[
                CustomerAppointment.STATUS_PENDING,
                CustomerAppointment.STATUS_APPROVED
            ]
        ).select_related('appointment', 'customer', 'appointment__staff', 'appointment__service')
        
        # Check if reminder already sent
        for appointment in appointments:
            # Check if reminder was already sent for this notification
            already_sent = appointment.sent_notifications.filter(
                notification=notification,
                status='sent'
            ).exists()
            
            if not already_sent:
                try:
                    result = sender_service.send_notification(notification, appointment)
                    if result.get('success'):
                        sent_count += 1
                        logger.info(f"Reminder sent for appointment #{appointment.id}")
                    else:
                        error_count += 1
                        logger.error(f"Failed to send reminder for appointment #{appointment.id}: {result.get('error')}")
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error sending reminder for appointment #{appointment.id}: {str(e)}")
    
    logger.info(f"Reminder task completed: {sent_count} sent, {error_count} errors")
    return {
        'sent': sent_count,
        'errors': error_count
    }


@shared_task
def send_follow_up_notifications():
    """
    Celery task to send follow-up notifications after appointments.
    Runs periodically to check for completed appointments that need follow-ups.
    """
    sender_service = NotificationSender()
    
    # Get all active follow-up notifications
    follow_up_notifications = Notification.objects.filter(
        event_type=Notification.EVENT_FOLLOW_UP,
        active=True
    )
    
    if not follow_up_notifications.exists():
        logger.info("No active follow-up notifications configured")
        return
    
    # Get appointments that ended in the last 24 hours
    now = timezone.now()
    yesterday = now - timedelta(hours=24)
    
    appointments = CustomerAppointment.objects.filter(
        appointment__end_date__gte=yesterday,
        appointment__end_date__lte=now,
        status=CustomerAppointment.STATUS_APPROVED
    ).select_related('appointment', 'customer', 'appointment__staff', 'appointment__service')
    
    sent_count = 0
    error_count = 0
    
    for notification in follow_up_notifications:
        for appointment in appointments:
            # Check if follow-up already sent
            already_sent = appointment.sent_notifications.filter(
                notification=notification,
                status='sent'
            ).exists()
            
            if not already_sent:
                try:
                    result = sender_service.send_notification(notification, appointment)
                    if result.get('success'):
                        sent_count += 1
                        logger.info(f"Follow-up sent for appointment #{appointment.id}")
                    else:
                        error_count += 1
                        logger.error(f"Failed to send follow-up for appointment #{appointment.id}: {result.get('error')}")
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error sending follow-up for appointment #{appointment.id}: {str(e)}")
    
    logger.info(f"Follow-up task completed: {sent_count} sent, {error_count} errors")
    return {
        'sent': sent_count,
        'errors': error_count
    }


@shared_task
def retry_failed_notifications():
    """
    Celery task to retry failed notifications.
    """
    from .models import SentNotification
    
    # Get failed notifications from the last 24 hours
    yesterday = timezone.now() - timedelta(hours=24)
    
    failed_notifications = SentNotification.objects.filter(
        status=SentNotification.STATUS_FAILED,
        created_at__gte=yesterday
    ).select_related('notification', 'customer_appointment')
    
    sender_service = NotificationSender()
    retried_count = 0
    success_count = 0
    
    for sent_notification in failed_notifications:
        try:
            result = sender_service.send_notification(
                sent_notification.notification,
                sent_notification.customer_appointment,
                recipient_email=sent_notification.recipient if '@' in sent_notification.recipient else None,
                recipient_phone=sent_notification.recipient if '@' not in sent_notification.recipient else None
            )
            
            if result.get('success'):
                success_count += 1
                logger.info(f"Retry successful for notification #{sent_notification.id}")
            else:
                logger.warning(f"Retry failed for notification #{sent_notification.id}: {result.get('error')}")
            
            retried_count += 1
            
        except Exception as e:
            logger.error(f"Error retrying notification #{sent_notification.id}: {str(e)}")
    
    logger.info(f"Retry task completed: {retried_count} retried, {success_count} successful")
    return {
        'retried': retried_count,
        'successful': success_count
    }

