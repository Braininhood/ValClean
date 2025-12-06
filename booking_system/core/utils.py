"""
Core utilities for the booking system.
"""
import qrcode
import logging
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from django.urls import reverse

logger = logging.getLogger(__name__)


def generate_qr_code(data, size=200):
    """
    Generate QR code image from data.
    
    Args:
        data: String data to encode in QR code
        size: Size of QR code image (default: 200x200)
    
    Returns:
        BytesIO: QR code image as BytesIO object
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Resize if needed
    if size != 200:
        img = img.resize((size, size))
    
    # Convert to BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return buffer


def generate_appointment_qr_code(appointment, customer_appointment=None, request=None):
    """
    Generate QR code for appointment with booking details.
    
    Args:
        appointment: Appointment instance
        customer_appointment: CustomerAppointment instance (optional)
        request: HttpRequest object (for building absolute URLs)
    
    Returns:
        BytesIO: QR code image
    """
    # Build appointment details URL
    if request:
        # Always use request.get_host() for accurate domain
        protocol = 'https' if request.is_secure() else 'http'
        domain = request.get_host()
    else:
        protocol = 'https' if not settings.DEBUG else 'http'
        # Try to get domain from Site framework, fallback to localhost
        try:
            from django.contrib.sites.models import Site
            current_site = Site.objects.get_current()
            domain = current_site.domain
        except Exception:
            domain = getattr(settings, 'DOMAIN', 'localhost:8000')
    
    # Create appointment details URL
    url = None
    if customer_appointment:
        # Try to use token if available
        if hasattr(customer_appointment, 'token') and customer_appointment.token:
            url = f"{protocol}://{domain}/appointments/view/{customer_appointment.token}/"
        else:
            # Generate token if not exists
            import secrets
            token = secrets.token_urlsafe(32)
            customer_appointment.token = token
            customer_appointment.save()
            url = f"{protocol}://{domain}/appointments/view/{token}/"
    
    if not url:
        # Fallback to appointment ID (requires authentication)
        url = f"{protocol}://{domain}/appointments/{appointment.id}/"
    
    # Create QR code data with appointment info
    qr_data = f"""APPOINTMENT DETAILS
Booking #: {customer_appointment.id if customer_appointment else appointment.id}
Service: {appointment.service.title}
Staff: {appointment.staff.full_name}
Date: {appointment.start_date.strftime('%Y-%m-%d %H:%M')}
Duration: {appointment.service.duration} minutes
Status: {customer_appointment.get_status_display() if customer_appointment else 'Confirmed'}

View Details: {url}"""
    
    return generate_qr_code(qr_data)


def get_appointment_links(appointment, customer_appointment=None, request=None):
    """
    Get all relevant links for an appointment.
    
    Args:
        appointment: Appointment instance
        customer_appointment: CustomerAppointment instance (optional)
        request: HttpRequest object (for building absolute URLs)
    
    Returns:
        dict: Dictionary with various appointment links
    """
    from urllib.parse import quote
    from django.utils import timezone
    
    if request:
        # Always use request.get_host() for accurate domain
        protocol = 'https' if request.is_secure() else 'http'
        domain = request.get_host()
    else:
        protocol = 'https' if not settings.DEBUG else 'http'
        # Try to get domain from Site framework, fallback to localhost
        try:
            from django.contrib.sites.models import Site
            current_site = Site.objects.get_current()
            domain = current_site.domain
        except Exception:
            domain = getattr(settings, 'DOMAIN', 'localhost:8000')
    
    base_url = f"{protocol}://{domain}"
    
    links = {
        'view': f"{base_url}/appointments/{appointment.id}/",
        'ical': f"{base_url}/calendar-sync/ical/{appointment.id}/",
    }
    
    if customer_appointment:
        if customer_appointment.token:
            links['view_public'] = f"{base_url}/appointments/view/{customer_appointment.token}/"
            links['cancel'] = f"{base_url}/appointments/cancel/{customer_appointment.token}/"
        
        links['customer_dashboard'] = f"{base_url}/customers/dashboard/"
    
    # Generate Google Calendar add event URL
    try:
        from django.utils import timezone as tz
        from datetime import timezone as dt_timezone
        # Convert to UTC for Google Calendar (YYYYMMDDTHHMMSSZ)
        start_utc = appointment.start_date
        if tz.is_aware(start_utc):
            start_utc = start_utc.astimezone(dt_timezone.utc)
        else:
            start_utc = tz.make_aware(start_utc, dt_timezone.utc)
        
        end_utc = appointment.end_date
        if tz.is_aware(end_utc):
            end_utc = end_utc.astimezone(dt_timezone.utc)
        else:
            end_utc = tz.make_aware(end_utc, dt_timezone.utc)
        
        start_str = start_utc.strftime('%Y%m%dT%H%M%SZ')
        end_str = end_utc.strftime('%Y%m%dT%H%M%SZ')
        
        # Build event details
        event_title = f"{appointment.service.title}"
        if customer_appointment and customer_appointment.customer:
            event_title += f" - {customer_appointment.customer.name}"
        title = quote(event_title)
        
        details_text = f"Service: {appointment.service.title}\nStaff: {appointment.staff.full_name}\nDuration: {appointment.service.duration} minutes"
        if customer_appointment and customer_appointment.customer:
            details_text += f"\nCustomer: {customer_appointment.customer.name}"
            if customer_appointment.customer.email:
                details_text += f"\nEmail: {customer_appointment.customer.email}"
        details = quote(details_text)
        
        location = ""
        if customer_appointment and customer_appointment.customer:
            location_parts = []
            if customer_appointment.customer.address_line1:
                location_parts.append(customer_appointment.customer.address_line1)
            if customer_appointment.customer.city:
                location_parts.append(customer_appointment.customer.city)
            if location_parts:
                location = quote(", ".join(location_parts))
        
        google_cal_url = (
            f"https://calendar.google.com/calendar/render?"
            f"action=TEMPLATE&"
            f"text={title}&"
            f"dates={start_str}/{end_str}&"
            f"details={details}"
        )
        if location:
            google_cal_url += f"&location={location}"
        
        links['google_calendar'] = google_cal_url
    except Exception as e:
        logger.error(f"Error generating Google Calendar URL: {str(e)}", exc_info=True)
        # Always create a basic URL as fallback
        try:
            from django.utils import timezone as tz
            from datetime import timezone as dt_timezone
            start_utc = appointment.start_date
            if tz.is_aware(start_utc):
                start_utc = start_utc.astimezone(dt_timezone.utc)
            else:
                start_utc = tz.make_aware(start_utc, dt_timezone.utc)
            end_utc = appointment.end_date
            if tz.is_aware(end_utc):
                end_utc = end_utc.astimezone(dt_timezone.utc)
            else:
                end_utc = tz.make_aware(end_utc, dt_timezone.utc)
            start_str = start_utc.strftime('%Y%m%dT%H%M%SZ')
            end_str = end_utc.strftime('%Y%m%dT%H%M%SZ')
            title = quote(f"{appointment.service.title}")
            links['google_calendar'] = (
                f"https://calendar.google.com/calendar/render?"
                f"action=TEMPLATE&"
                f"text={title}&"
                f"dates={start_str}/{end_str}"
            )
        except Exception as e2:
            logger.error(f"Fallback Google Calendar URL generation also failed: {str(e2)}")
            # Even if everything fails, create a minimal URL
            try:
                start_str = appointment.start_date.strftime('%Y%m%dT%H%M%SZ')
                end_str = appointment.end_date.strftime('%Y%m%dT%H%M%SZ')
                title = quote(f"{appointment.service.title}")
                links['google_calendar'] = (
                    f"https://calendar.google.com/calendar/render?"
                    f"action=TEMPLATE&"
                    f"text={title}&"
                    f"dates={start_str}/{end_str}"
                )
            except:
                links['google_calendar'] = None
    
    # Generate Outlook Calendar add event URL
    try:
        # Format dates for Outlook Calendar (ISO 8601)
        start_iso = appointment.start_date.isoformat()
        end_iso = appointment.end_date.isoformat()
        
        title = quote(f"{appointment.service.title} - {customer_appointment.customer.name if customer_appointment else 'Appointment'}")
        body = quote(f"Service: {appointment.service.title}\nStaff: {appointment.staff.full_name}\nDuration: {appointment.service.duration} minutes")
        location = ""
        if customer_appointment and customer_appointment.customer:
            location_parts = []
            if customer_appointment.customer.address_line1:
                location_parts.append(customer_appointment.customer.address_line1)
            if customer_appointment.customer.city:
                location_parts.append(customer_appointment.customer.city)
            if location_parts:
                location = quote(", ".join(location_parts))
        
        outlook_cal_url = (
            f"https://outlook.live.com/calendar/0/deeplink/compose?"
            f"subject={title}&"
            f"startdt={start_iso}&"
            f"enddt={end_iso}&"
            f"body={body}"
        )
        if location:
            outlook_cal_url += f"&location={location}"
        
        links['outlook_calendar'] = outlook_cal_url
    except Exception as e:
        logger.warning(f"Error generating Outlook Calendar URL: {str(e)}")
        # Still create a basic URL even if there's an error
        try:
            start_iso = appointment.start_date.isoformat()
            end_iso = appointment.end_date.isoformat()
            title = quote(f"{appointment.service.title}")
            links['outlook_calendar'] = (
                f"https://outlook.live.com/calendar/0/deeplink/compose?"
                f"subject={title}&"
                f"startdt={start_iso}&"
                f"enddt={end_iso}"
            )
        except:
            links['outlook_calendar'] = None
    
    return links

