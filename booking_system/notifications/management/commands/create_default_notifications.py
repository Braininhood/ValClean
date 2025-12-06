"""
Management command to create default notification templates.
"""
from django.core.management.base import BaseCommand
from notifications.models import Notification


class Command(BaseCommand):
    help = 'Create default notification templates'

    def handle(self, *args, **options):
        """Create default notification templates."""
        
        default_notifications = [
            # New appointment - Customer
            {
                'type': Notification.TYPE_EMAIL,
                'event_type': Notification.EVENT_NEW,
                'send_to': Notification.SEND_TO_CUSTOMER,
                'subject': 'Appointment Confirmation - {service_name}',
                'message': '''Dear {customer_name},

Thank you for booking an appointment with us!

Appointment Details:
- Service: {service_name}
- Staff: {staff_name}
- Date & Time: {appointment_datetime}
- Duration: {service_duration} minutes
- Booking Number: {booking_number}

Your appointment is currently pending approval. You will receive a confirmation once it's approved.

{cancellation_link}

We look forward to seeing you!

Best regards,
Booking System''',
                'active': True,
            },
            # New appointment - Staff
            {
                'type': Notification.TYPE_EMAIL,
                'event_type': Notification.EVENT_NEW,
                'send_to': Notification.SEND_TO_STAFF,
                'subject': 'New Appointment Booking - {service_name}',
                'message': '''Hello {staff_name},

A new appointment has been booked:

Customer: {customer_name}
Service: {service_name}
Date & Time: {appointment_datetime}
Duration: {service_duration} minutes
Booking Number: {booking_number}

Please review and approve this appointment in your dashboard.

Best regards,
Booking System''',
                'active': True,
            },
            # Approved appointment - Customer
            {
                'type': Notification.TYPE_EMAIL,
                'event_type': Notification.EVENT_APPROVED,
                'send_to': Notification.SEND_TO_CUSTOMER,
                'subject': 'Appointment Approved - {service_name}',
                'message': '''Dear {customer_name},

Great news! Your appointment has been approved.

Appointment Details:
- Service: {service_name}
- Staff: {staff_name}
- Date & Time: {appointment_datetime}
- Duration: {service_duration} minutes
- Booking Number: {booking_number}

We look forward to seeing you on {appointment_date} at {appointment_time}.

{cancellation_link}

Best regards,
Booking System''',
                'active': True,
            },
            # Cancelled appointment - Customer
            {
                'type': Notification.TYPE_EMAIL,
                'event_type': Notification.EVENT_CANCELLED,
                'send_to': Notification.SEND_TO_CUSTOMER,
                'subject': 'Appointment Cancelled - {service_name}',
                'message': '''Dear {customer_name},

Your appointment has been cancelled.

Appointment Details:
- Service: {service_name}
- Staff: {staff_name}
- Date & Time: {appointment_datetime}
- Booking Number: {booking_number}

If you would like to reschedule, please book a new appointment.

Best regards,
Booking System''',
                'active': True,
            },
            # Reminder - Customer (24 hours before)
            {
                'type': Notification.TYPE_EMAIL,
                'event_type': Notification.EVENT_REMINDER,
                'send_to': Notification.SEND_TO_CUSTOMER,
                'subject': 'Appointment Reminder - {service_name}',
                'message': '''Dear {customer_name},

This is a reminder about your upcoming appointment:

Service: {service_name}
Staff: {staff_name}
Date & Time: {appointment_datetime}
Duration: {service_duration} minutes

We look forward to seeing you!

{cancellation_link}

Best regards,
Booking System''',
                'active': True,
                'reminder_hours_before': 24,
            },
            # Reminder - Customer (SMS, 2 hours before)
            {
                'type': Notification.TYPE_SMS,
                'event_type': Notification.EVENT_REMINDER,
                'send_to': Notification.SEND_TO_CUSTOMER,
                'subject': '',
                'message': 'Reminder: You have an appointment for {service_name} with {staff_name} on {appointment_datetime}. Booking #{booking_number}',
                'active': True,
                'reminder_hours_before': 2,
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for notification_data in default_notifications:
            notification, created = Notification.objects.update_or_create(
                type=notification_data['type'],
                event_type=notification_data['event_type'],
                send_to=notification_data['send_to'],
                defaults={
                    'subject': notification_data.get('subject', ''),
                    'message': notification_data['message'],
                    'active': notification_data.get('active', True),
                    'reminder_hours_before': notification_data.get('reminder_hours_before'),
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {notification}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated: {notification}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted: {created_count} created, {updated_count} updated'
            )
        )

