"""
Notification services for sending emails and SMS.
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class EmailNotificationService:
    """Service for sending email notifications."""
    
    def __init__(self):
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@booking-system.com')
    
    def send_email(self, recipient_email, subject, message_html, message_text=None, attachments=None):
        """
        Send an email notification.
        
        Args:
            recipient_email: Email address of recipient
            subject: Email subject
            message_html: HTML content of email
            message_text: Plain text version (optional, auto-generated if not provided)
            attachments: List of attachments (optional)
        
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            # Generate plain text from HTML if not provided
            if not message_text:
                message_text = strip_tags(message_html)
            
            # Create email message
            email = EmailMultiAlternatives(
                subject=subject,
                body=message_text,
                from_email=self.from_email,
                to=[recipient_email]
            )
            
            # Attach HTML version
            email.attach_alternative(message_html, "text/html")
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    email.attach(*attachment)
            
            # Send email
            email.send()
            
            logger.info(f"Email sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
            return False
    
    def send_bulk_emails(self, recipients, subject, message_html, message_text=None):
        """
        Send emails to multiple recipients.
        
        Args:
            recipients: List of email addresses
            subject: Email subject
            message_html: HTML content
            message_text: Plain text version
        
        Returns:
            dict: Results with recipient as key and success status as value
        """
        results = {}
        for recipient in recipients:
            results[recipient] = self.send_email(recipient, subject, message_html, message_text)
        return results


class SMSNotificationService:
    """Service for sending SMS notifications via Twilio."""
    
    def __init__(self):
        self.account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
        self.auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
        self.phone_number = getattr(settings, 'TWILIO_PHONE_NUMBER', '')
        self.enabled = bool(self.account_sid and self.auth_token and self.phone_number)
    
    def send_sms(self, recipient_phone, message):
        """
        Send an SMS notification via Twilio.
        
        Args:
            recipient_phone: Phone number of recipient (E.164 format)
            message: SMS message text
        
        Returns:
            dict: Result with 'success', 'message_sid', and 'error' keys
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'Twilio is not configured. Please add TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER to settings.'
            }
        
        try:
            from twilio.rest import Client
            
            client = Client(self.account_sid, self.auth_token)
            
            # Send SMS
            message_obj = client.messages.create(
                body=message,
                from_=self.phone_number,
                to=recipient_phone
            )
            
            logger.info(f"SMS sent successfully to {recipient_phone}, SID: {message_obj.sid}")
            
            return {
                'success': True,
                'message_sid': message_obj.sid,
                'status': message_obj.status,
            }
            
        except ImportError:
            return {
                'success': False,
                'error': 'Twilio library not installed. Install with: pip install twilio'
            }
        except Exception as e:
            logger.error(f"Failed to send SMS to {recipient_phone}: {str(e)}")
            return {
                'success': False,
                'error': f'Twilio error: {str(e)}'
            }
    
    def send_bulk_sms(self, recipients, message):
        """
        Send SMS to multiple recipients.
        
        Args:
            recipients: List of phone numbers
            message: SMS message text
        
        Returns:
            dict: Results with recipient as key and result dict as value
        """
        results = {}
        for recipient in recipients:
            results[recipient] = self.send_sms(recipient, message)
        return results


class NotificationTemplateRenderer:
    """Service for rendering notification templates with placeholders."""
    
    # Available placeholders for templates
    PLACEHOLDERS = {
        'customer_name': 'Customer full name',
        'customer_email': 'Customer email address',
        'customer_phone': 'Customer phone number',
        'staff_name': 'Staff member full name',
        'staff_email': 'Staff member email',
        'staff_phone': 'Staff member phone',
        'service_name': 'Service title',
        'service_duration': 'Service duration in minutes',
        'appointment_date': 'Appointment date (formatted)',
        'appointment_time': 'Appointment time (formatted)',
        'appointment_datetime': 'Full appointment date and time',
        'appointment_status': 'Appointment status',
        'booking_number': 'Booking reference number',
        'payment_amount': 'Payment amount',
        'payment_status': 'Payment status',
        'cancellation_link': 'Link to cancel appointment',
        'reschedule_link': 'Link to reschedule appointment',
    }
    
    @staticmethod
    def render_template(template_text, context):
        """
        Render notification template with placeholders.
        
        Args:
            template_text: Template text with placeholders like {customer_name}
            context: Dictionary with placeholder values
        
        Returns:
            str: Rendered template text
        """
        try:
            # Simple placeholder replacement
            rendered = template_text
            for key, value in context.items():
                placeholder = '{' + key + '}'
                rendered = rendered.replace(placeholder, str(value or ''))
            
            return rendered
        except Exception as e:
            logger.error(f"Error rendering template: {str(e)}")
            return template_text
    
    @staticmethod
    def get_appointment_context(customer_appointment):
        """
        Get context dictionary for appointment-based notifications.
        
        Args:
            customer_appointment: CustomerAppointment instance
        
        Returns:
            dict: Context with all available placeholders
        """
        appointment = customer_appointment.appointment
        customer = customer_appointment.customer
        staff = appointment.staff
        service = appointment.service
        
        # Format datetime
        appointment_datetime = appointment.start_date
        appointment_date = appointment_datetime.strftime('%B %d, %Y') if appointment_datetime else ''
        appointment_time = appointment_datetime.strftime('%I:%M %p') if appointment_datetime else ''
        appointment_datetime_str = appointment_datetime.strftime('%B %d, %Y at %I:%M %p') if appointment_datetime else ''
        
        # Payment info
        payment_amount = ''
        payment_status = ''
        if customer_appointment.payment:
            payment_amount = f"£{customer_appointment.payment.total}"
            payment_status = customer_appointment.payment.get_status_display()
        
        # Cancellation link (if token exists)
        cancellation_link = ''
        if customer_appointment.token:
            from django.urls import reverse
            from django.contrib.sites.models import Site
            try:
                current_site = Site.objects.get_current()
                domain = current_site.domain
                protocol = 'https' if not settings.DEBUG else 'http'
                cancellation_link = f"{protocol}://{domain}{reverse('appointments:cancel_appointment', args=[customer_appointment.token])}"
            except:
                cancellation_link = f"Cancel link (token: {customer_appointment.token})"
        
        context = {
            'customer_name': customer.name if customer else '',
            'customer_email': customer.email if customer else '',
            'customer_phone': customer.phone if customer else '',
            'staff_name': staff.full_name if staff else '',
            'staff_email': staff.email if staff else '',
            'staff_phone': staff.phone if staff else '',
            'service_name': service.title if service else '',
            'service_duration': service.duration if service else '',
            'appointment_date': appointment_date,
            'appointment_time': appointment_time,
            'appointment_datetime': appointment_datetime_str,
            'appointment_status': customer_appointment.get_status_display(),
            'booking_number': f"#{customer_appointment.id}",
            'payment_amount': payment_amount,
            'payment_status': payment_status,
            'cancellation_link': cancellation_link,
            'reschedule_link': '',  # TODO: Implement reschedule link
        }
        
        return context


class NotificationSender:
    """Main service for sending notifications based on Notification templates."""
    
    def __init__(self):
        self.email_service = EmailNotificationService()
        self.sms_service = SMSNotificationService()
        self.template_renderer = NotificationTemplateRenderer()
    
    def send_notification(self, notification, customer_appointment, recipient_email=None, recipient_phone=None):
        """
        Send a notification based on Notification template.
        
        Args:
            notification: Notification instance (template)
            customer_appointment: CustomerAppointment instance
            recipient_email: Override recipient email (optional)
            recipient_phone: Override recipient phone (optional)
        
        Returns:
            dict: Result with 'success', 'sent_notification', and 'error' keys
        """
        from .models import SentNotification
        
        # Get context for template rendering
        context = self.template_renderer.get_appointment_context(customer_appointment)
        
        # Determine recipient
        if notification.send_to == 'customer':
            recipient_email = recipient_email or customer_appointment.customer.email
            recipient_phone = recipient_phone or customer_appointment.customer.phone
        elif notification.send_to == 'staff':
            recipient_email = recipient_email or customer_appointment.appointment.staff.email
            recipient_phone = recipient_phone or customer_appointment.appointment.staff.phone
        elif notification.send_to == 'admin':
            # Get admin email from settings
            recipient_email = recipient_email or getattr(settings, 'ADMIN_EMAIL', self.email_service.from_email)
            recipient_phone = recipient_phone or ''
        
        # Render template
        rendered_message = self.template_renderer.render_template(notification.message, context)
        rendered_subject = self.template_renderer.render_template(notification.subject or 'Appointment Notification', context)
        
        # Create sent notification record
        sent_notification = SentNotification.objects.create(
            notification=notification,
            customer_appointment=customer_appointment,
            recipient=recipient_email or recipient_phone or '',
            status=SentNotification.STATUS_PENDING,
        )
        
        success = False
        error_message = ''
        
        try:
            if notification.type == 'email':
                if recipient_email:
                    success = self.email_service.send_email(
                        recipient_email,
                        rendered_subject,
                        rendered_message,  # For now, treat as HTML
                    )
                    if success:
                        sent_notification.status = SentNotification.STATUS_SENT
                        sent_notification.sent_at = timezone.now()
                    else:
                        sent_notification.status = SentNotification.STATUS_FAILED
                        error_message = 'Email sending failed'
                else:
                    error_message = 'No recipient email provided'
                    sent_notification.status = SentNotification.STATUS_FAILED
            
            elif notification.type == 'sms':
                if recipient_phone:
                    result = self.sms_service.send_sms(recipient_phone, rendered_message)
                    if result.get('success'):
                        sent_notification.status = SentNotification.STATUS_SENT
                        sent_notification.sent_at = timezone.now()
                        success = True
                    else:
                        sent_notification.status = SentNotification.STATUS_FAILED
                        error_message = result.get('error', 'SMS sending failed')
                else:
                    error_message = 'No recipient phone provided'
                    sent_notification.status = SentNotification.STATUS_FAILED
            
            if error_message:
                sent_notification.error_message = error_message
            
            sent_notification.save()
            
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            sent_notification.status = SentNotification.STATUS_FAILED
            sent_notification.error_message = str(e)
            sent_notification.save()
            success = False
            error_message = str(e)
        
        return {
            'success': success,
            'sent_notification': sent_notification,
            'error': error_message,
        }
    
    def send_appointment_notifications(self, customer_appointment, event_type):
        """
        Send all active notifications for a specific appointment event.
        
        Args:
            customer_appointment: CustomerAppointment instance
            event_type: Event type (e.g., 'new', 'approved', 'cancelled')
        
        Returns:
            list: List of result dictionaries
        """
        from .models import Notification
        
        # Get all active notifications for this event type
        notifications = Notification.objects.filter(
            event_type=event_type,
            active=True
        )
        
        results = []
        for notification in notifications:
            result = self.send_notification(notification, customer_appointment)
            results.append(result)
        
        return results

