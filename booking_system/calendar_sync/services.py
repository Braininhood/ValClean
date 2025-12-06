"""
Calendar sync services for Google, Outlook, and Apple calendars.
"""
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class BaseCalendarService:
    """Base class for calendar services."""
    
    def __init__(self, staff):
        self.staff = staff
        self.provider_name = None
    
    def authenticate(self):
        """Authenticate with calendar provider. Returns True if authenticated."""
        raise NotImplementedError("Subclasses must implement authenticate")
    
    def create_event(self, appointment, customer_appointment=None):
        """
        Create calendar event for appointment.
        
        Args:
            appointment: Appointment instance
            customer_appointment: CustomerAppointment instance (optional)
        
        Returns:
            dict: {'success': bool, 'event_id': str, 'error': str}
        """
        raise NotImplementedError("Subclasses must implement create_event")
    
    def update_event(self, appointment, event_id, customer_appointment=None):
        """
        Update existing calendar event.
        
        Args:
            appointment: Appointment instance
            event_id: Calendar event ID
            customer_appointment: CustomerAppointment instance (optional)
        
        Returns:
            dict: {'success': bool, 'error': str}
        """
        raise NotImplementedError("Subclasses must implement update_event")
    
    def delete_event(self, event_id):
        """
        Delete calendar event.
        
        Args:
            event_id: Calendar event ID
        
        Returns:
            dict: {'success': bool, 'error': str}
        """
        raise NotImplementedError("Subclasses must implement delete_event")
    
    def get_busy_times(self, start_date, end_date):
        """
        Get busy times from calendar (for two-way sync).
        
        Args:
            start_date: Start datetime
            end_date: End datetime
        
        Returns:
            list: List of busy time ranges
        """
        raise NotImplementedError("Subclasses must implement get_busy_times")
    
    def format_event_description(self, appointment, customer_appointment=None, request=None):
        """Format event description with appointment details and links."""
        from django.conf import settings
        
        description_parts = []
        
        # Booking reference
        if customer_appointment:
            description_parts.append(f"Booking Reference: #{customer_appointment.id}")
        else:
            description_parts.append(f"Appointment ID: #{appointment.id}")
        
        description_parts.append("")  # Empty line
        
        # Customer information
        if customer_appointment:
            description_parts.append(f"Customer: {customer_appointment.customer.name}")
            description_parts.append(f"Email: {customer_appointment.customer.email}")
            if customer_appointment.customer.phone:
                description_parts.append(f"Phone: {customer_appointment.customer.phone}")
            description_parts.append(f"Number of persons: {customer_appointment.number_of_persons}")
            description_parts.append("")  # Empty line
        
        # Service information
        description_parts.append(f"Service: {appointment.service.title}")
        description_parts.append(f"Duration: {appointment.service.duration} minutes")
        description_parts.append(f"Staff: {appointment.staff.full_name}")
        description_parts.append("")  # Empty line
        
        # Appointment status
        if customer_appointment:
            description_parts.append(f"Status: {customer_appointment.get_status_display()}")
            description_parts.append("")  # Empty line
        
        # Links
        try:
            if request:
                protocol = 'https' if request.is_secure() else 'http'
                domain = request.get_host()
            else:
                try:
                    from django.contrib.sites.models import Site
                    current_site = Site.objects.get_current()
                    domain = current_site.domain
                    protocol = 'https' if not settings.DEBUG else 'http'
                except Exception:
                    # Fallback if sites framework not configured
                    protocol = 'https' if not settings.DEBUG else 'http'
                    domain = getattr(settings, 'DOMAIN', 'localhost:8000')
            
            base_url = f"{protocol}://{domain}"
            
            description_parts.append("--- Links ---")
            description_parts.append(f"View Appointment: {base_url}/appointments/{appointment.id}/")
            description_parts.append(f"Download Calendar: {base_url}/calendar-sync/ical/{appointment.id}/")
            
            if customer_appointment and customer_appointment.token:
                description_parts.append(f"View Details: {base_url}/appointments/view/{customer_appointment.token}/")
                description_parts.append(f"Cancel Appointment: {base_url}/appointments/cancel/{customer_appointment.token}/")
            
        except Exception as e:
            logger.warning(f"Error generating links in calendar description: {str(e)}")
        
        # Internal note
        if appointment.internal_note:
            description_parts.append("")  # Empty line
            description_parts.append(f"Internal Note: {appointment.internal_note}")
        
        return "\n".join(description_parts)


class GoogleCalendarService(BaseCalendarService):
    """Google Calendar integration service."""
    
    def __init__(self, staff):
        super().__init__(staff)
        self.provider_name = 'google'
        self.client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '')
        self.client_secret = getattr(settings, 'GOOGLE_CLIENT_SECRET', '')
        self.redirect_uri = getattr(settings, 'GOOGLE_REDIRECT_URI', '')
        self.scope = 'https://www.googleapis.com/auth/calendar'
    
    def authenticate(self):
        """Check if staff has valid Google Calendar credentials."""
        calendar_data = self.staff.calendar_data or {}
        access_token = calendar_data.get('access_token')
        refresh_token = calendar_data.get('refresh_token')
        
        if not access_token or not refresh_token:
            return False
        
        # Check if token is expired and refresh if needed
        expires_at = calendar_data.get('expires_at')
        if expires_at:
            from datetime import datetime
            if isinstance(expires_at, str):
                expires_at = datetime.fromisoformat(expires_at)
            if expires_at < timezone.now():
                return self.refresh_access_token()
        
        return True
    
    def refresh_access_token(self):
        """Refresh Google OAuth access token."""
        try:
            import requests
            
            calendar_data = self.staff.calendar_data or {}
            refresh_token = calendar_data.get('refresh_token')
            
            if not refresh_token:
                return False
            
            token_url = 'https://oauth2.googleapis.com/token'
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token',
            }
            
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Update calendar_data
            calendar_data['access_token'] = token_data['access_token']
            calendar_data['expires_at'] = (
                timezone.now() + timedelta(seconds=token_data.get('expires_in', 3600))
            ).isoformat()
            
            self.staff.calendar_data = calendar_data
            self.staff.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Error refreshing Google token: {str(e)}")
            return False
    
    def get_access_token(self):
        """Get valid access token."""
        if not self.authenticate():
            return None
        
        calendar_data = self.staff.calendar_data or {}
        return calendar_data.get('access_token')
    
    def create_event(self, appointment, customer_appointment=None):
        """Create Google Calendar event."""
        access_token = self.get_access_token()
        if not access_token:
            return {
                'success': False,
                'error': 'Not authenticated with Google Calendar. Please connect your calendar.'
            }
        
        try:
            import requests
            
            calendar_id = self.staff.calendar_id or 'primary'
            
            # Format event data
            event_data = {
                'summary': f"{appointment.service.title} - {customer_appointment.customer.name if customer_appointment else 'Appointment'}",
                'description': self.format_event_description(appointment, customer_appointment, None),
                'start': {
                    'dateTime': appointment.start_date.isoformat(),
                    'timeZone': str(appointment.start_date.tzinfo) if appointment.start_date.tzinfo else 'UTC',
                },
                'end': {
                    'dateTime': appointment.end_date.isoformat(),
                    'timeZone': str(appointment.end_date.tzinfo) if appointment.end_date.tzinfo else 'UTC',
                },
                'location': '',  # Can be added from customer address
            }
            
            # Add attendees if customer email available
            if customer_appointment and customer_appointment.customer.email:
                event_data['attendees'] = [
                    {'email': customer_appointment.customer.email}
                ]
            
            url = f'https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events'
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            }
            
            response = requests.post(url, json=event_data, headers=headers)
            response.raise_for_status()
            
            event = response.json()
            
            return {
                'success': True,
                'event_id': event['id'],
            }
            
        except ImportError:
            return {
                'success': False,
                'error': 'Requests library not installed. Install with: pip install requests'
            }
        except Exception as e:
            logger.error(f"Error creating Google Calendar event: {str(e)}")
            return {
                'success': False,
                'error': f'Google Calendar error: {str(e)}'
            }
    
    def update_event(self, appointment, event_id, customer_appointment=None, request=None):
        """Update Google Calendar event."""
        access_token = self.get_access_token()
        if not access_token:
            return {
                'success': False,
                'error': 'Not authenticated with Google Calendar.'
            }
        
        try:
            import requests
            
            calendar_id = self.staff.calendar_id or 'primary'
            
            event_data = {
                'summary': f"{appointment.service.title} - {customer_appointment.customer.name if customer_appointment else 'Appointment'}",
                'description': self.format_event_description(appointment, customer_appointment, request),
                'start': {
                    'dateTime': appointment.start_date.isoformat(),
                    'timeZone': str(appointment.start_date.tzinfo) if appointment.start_date.tzinfo else 'UTC',
                },
                'end': {
                    'dateTime': appointment.end_date.isoformat(),
                    'timeZone': str(appointment.end_date.tzinfo) if appointment.end_date.tzinfo else 'UTC',
                },
            }
            
            url = f'https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events/{event_id}'
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            }
            
            response = requests.put(url, json=event_data, headers=headers)
            response.raise_for_status()
            
            return {
                'success': True,
            }
            
        except Exception as e:
            logger.error(f"Error updating Google Calendar event: {str(e)}")
            return {
                'success': False,
                'error': f'Google Calendar error: {str(e)}'
            }
    
    def delete_event(self, event_id):
        """Delete Google Calendar event."""
        access_token = self.get_access_token()
        if not access_token:
            return {
                'success': False,
                'error': 'Not authenticated with Google Calendar.'
            }
        
        try:
            import requests
            
            calendar_id = self.staff.calendar_id or 'primary'
            
            url = f'https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events/{event_id}'
            headers = {
                'Authorization': f'Bearer {access_token}',
            }
            
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            
            return {
                'success': True,
            }
            
        except Exception as e:
            logger.error(f"Error deleting Google Calendar event: {str(e)}")
            return {
                'success': False,
                'error': f'Google Calendar error: {str(e)}'
            }
    
    def get_busy_times(self, start_date, end_date):
        """Get busy times from Google Calendar."""
        access_token = self.get_access_token()
        if not access_token:
            return []
        
        try:
            import requests
            
            calendar_id = self.staff.calendar_id or 'primary'
            
            url = 'https://www.googleapis.com/calendar/v3/freeBusy'
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            }
            
            data = {
                'timeMin': start_date.isoformat(),
                'timeMax': end_date.isoformat(),
                'items': [{'id': calendar_id}],
            }
            
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            busy_times = []
            
            for calendar_id_key, calendar_data in result.get('calendars', {}).items():
                for busy_period in calendar_data.get('busy', []):
                    busy_times.append({
                        'start': busy_period['start'],
                        'end': busy_period['end'],
                    })
            
            return busy_times
            
        except Exception as e:
            logger.error(f"Error getting Google Calendar busy times: {str(e)}")
            return []


class OutlookCalendarService(BaseCalendarService):
    """Microsoft Outlook Calendar integration service."""
    
    def __init__(self, staff):
        super().__init__(staff)
        self.provider_name = 'outlook'
        self.client_id = getattr(settings, 'MICROSOFT_CLIENT_ID', '')
        self.client_secret = getattr(settings, 'MICROSOFT_CLIENT_SECRET', '')
        self.tenant_id = getattr(settings, 'MICROSOFT_TENANT_ID', 'common')
        self.redirect_uri = getattr(settings, 'MICROSOFT_REDIRECT_URI', '')
    
    def authenticate(self):
        """Check if staff has valid Microsoft credentials."""
        calendar_data = self.staff.calendar_data or {}
        access_token = calendar_data.get('access_token')
        refresh_token = calendar_data.get('refresh_token')
        
        if not access_token or not refresh_token:
            return False
        
        # Check if token is expired and refresh if needed
        expires_at = calendar_data.get('expires_at')
        if expires_at:
            from datetime import datetime
            if isinstance(expires_at, str):
                expires_at = datetime.fromisoformat(expires_at)
            if expires_at < timezone.now():
                return self.refresh_access_token()
        
        return True
    
    def refresh_access_token(self):
        """Refresh Microsoft OAuth access token."""
        try:
            import requests
            
            calendar_data = self.staff.calendar_data or {}
            refresh_token = calendar_data.get('refresh_token')
            
            if not refresh_token:
                return False
            
            token_url = f'https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token'
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token',
                'scope': 'https://graph.microsoft.com/Calendars.ReadWrite',
            }
            
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Update calendar_data
            calendar_data['access_token'] = token_data['access_token']
            calendar_data['expires_at'] = (
                timezone.now() + timedelta(seconds=token_data.get('expires_in', 3600))
            ).isoformat()
            
            self.staff.calendar_data = calendar_data
            self.staff.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Error refreshing Microsoft token: {str(e)}")
            return False
    
    def get_access_token(self):
        """Get valid access token."""
        if not self.authenticate():
            return None
        
        calendar_data = self.staff.calendar_data or {}
        return calendar_data.get('access_token')
    
    def create_event(self, appointment, customer_appointment=None):
        """Create Outlook Calendar event."""
        access_token = self.get_access_token()
        if not access_token:
            return {
                'success': False,
                'error': 'Not authenticated with Microsoft Outlook. Please connect your calendar.'
            }
        
        try:
            import requests
            
            # Format event data
            event_data = {
                'subject': f"{appointment.service.title} - {customer_appointment.customer.name if customer_appointment else 'Appointment'}",
                'body': {
                    'contentType': 'Text',
                    'content': self.format_event_description(appointment, customer_appointment, None),
                },
                'start': {
                    'dateTime': appointment.start_date.isoformat(),
                    'timeZone': str(appointment.start_date.tzinfo) if appointment.start_date.tzinfo else 'UTC',
                },
                'end': {
                    'dateTime': appointment.end_date.isoformat(),
                    'timeZone': str(appointment.end_date.tzinfo) if appointment.end_date.tzinfo else 'UTC',
                },
            }
            
            # Add attendees if customer email available
            if customer_appointment and customer_appointment.customer.email:
                event_data['attendees'] = [
                    {
                        'emailAddress': {
                            'address': customer_appointment.customer.email,
                            'name': customer_appointment.customer.name,
                        },
                        'type': 'required',
                    }
                ]
            
            url = 'https://graph.microsoft.com/v1.0/me/calendar/events'
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            }
            
            response = requests.post(url, json=event_data, headers=headers)
            response.raise_for_status()
            
            event = response.json()
            
            return {
                'success': True,
                'event_id': event['id'],
            }
            
        except Exception as e:
            logger.error(f"Error creating Outlook Calendar event: {str(e)}")
            return {
                'success': False,
                'error': f'Outlook Calendar error: {str(e)}'
            }
    
    def update_event(self, appointment, event_id, customer_appointment=None, request=None):
        """Update Outlook Calendar event."""
        access_token = self.get_access_token()
        if not access_token:
            return {
                'success': False,
                'error': 'Not authenticated with Microsoft Outlook.'
            }
        
        try:
            import requests
            
            event_data = {
                'subject': f"{appointment.service.title} - {customer_appointment.customer.name if customer_appointment else 'Appointment'}",
                'body': {
                    'contentType': 'Text',
                    'content': self.format_event_description(appointment, customer_appointment, request),
                },
                'start': {
                    'dateTime': appointment.start_date.isoformat(),
                    'timeZone': str(appointment.start_date.tzinfo) if appointment.start_date.tzinfo else 'UTC',
                },
                'end': {
                    'dateTime': appointment.end_date.isoformat(),
                    'timeZone': str(appointment.end_date.tzinfo) if appointment.end_date.tzinfo else 'UTC',
                },
            }
            
            url = f'https://graph.microsoft.com/v1.0/me/calendar/events/{event_id}'
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            }
            
            response = requests.patch(url, json=event_data, headers=headers)
            response.raise_for_status()
            
            return {
                'success': True,
            }
            
        except Exception as e:
            logger.error(f"Error updating Outlook Calendar event: {str(e)}")
            return {
                'success': False,
                'error': f'Outlook Calendar error: {str(e)}'
            }
    
    def delete_event(self, event_id):
        """Delete Outlook Calendar event."""
        access_token = self.get_access_token()
        if not access_token:
            return {
                'success': False,
                'error': 'Not authenticated with Microsoft Outlook.'
            }
        
        try:
            import requests
            
            url = f'https://graph.microsoft.com/v1.0/me/calendar/events/{event_id}'
            headers = {
                'Authorization': f'Bearer {access_token}',
            }
            
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            
            return {
                'success': True,
            }
            
        except Exception as e:
            logger.error(f"Error deleting Outlook Calendar event: {str(e)}")
            return {
                'success': False,
                'error': f'Outlook Calendar error: {str(e)}'
            }
    
    def get_busy_times(self, start_date, end_date):
        """Get busy times from Outlook Calendar."""
        access_token = self.get_access_token()
        if not access_token:
            return []
        
        try:
            import requests
            
            url = 'https://graph.microsoft.com/v1.0/me/calendar/getSchedule'
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            }
            
            data = {
                'schedules': ['me'],
                'startTime': {
                    'dateTime': start_date.isoformat(),
                    'timeZone': str(start_date.tzinfo) if start_date.tzinfo else 'UTC',
                },
                'endTime': {
                    'dateTime': end_date.isoformat(),
                    'timeZone': str(end_date.tzinfo) if end_date.tzinfo else 'UTC',
                },
                'availabilityViewInterval': 60,
            }
            
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            busy_times = []
            
            for schedule in result.get('value', []):
                for item in schedule.get('scheduleItems', []):
                    if item.get('status') == 'busy':
                        busy_times.append({
                            'start': item['start']['dateTime'],
                            'end': item['end']['dateTime'],
                        })
            
            return busy_times
            
        except Exception as e:
            logger.error(f"Error getting Outlook Calendar busy times: {str(e)}")
            return []


class AppleCalendarService(BaseCalendarService):
    """Apple Calendar integration service (CalDAV/iCal)."""
    
    def __init__(self, staff):
        super().__init__(staff)
        self.provider_name = 'apple'
    
    def authenticate(self):
        """Apple Calendar uses CalDAV - check if credentials are configured."""
        calendar_data = self.staff.calendar_data or {}
        caldav_url = calendar_data.get('caldav_url')
        username = calendar_data.get('username')
        password = calendar_data.get('password')
        
        return bool(caldav_url and username and password)
    
    def create_event(self, appointment, customer_appointment=None, request=None):
        """Create Apple Calendar event via CalDAV."""
        # For Apple Calendar, we'll generate iCal file and provide download
        # Actual CalDAV sync requires server setup
        return {
            'success': True,
            'event_id': f"ical_{appointment.id}",
            'ical_file': self.generate_ical_file(appointment, customer_appointment, request),
        }
    
    def generate_ical_file(self, appointment, customer_appointment=None, request=None):
        """Generate iCal (.ics) file content."""
        try:
            from icalendar import Calendar, Event
            from datetime import datetime
            
            cal = Calendar()
            cal.add('prodid', '-//Booking System//EN')
            cal.add('version', '2.0')
            
            event = Event()
            event.add('summary', f"{appointment.service.title} - {customer_appointment.customer.name if customer_appointment else 'Appointment'}")
            event.add('description', self.format_event_description(appointment, customer_appointment, request))
            event.add('dtstart', appointment.start_date)
            event.add('dtend', appointment.end_date)
            event.add('dtstamp', timezone.now())
            event.add('uid', f"appointment-{appointment.id}@booking-system.com")
            
            if customer_appointment and customer_appointment.customer.email:
                event.add('attendee', f"mailto:{customer_appointment.customer.email}")
            
            cal.add_component(event)
            
            return cal.to_ical().decode('utf-8')
            
        except ImportError:
            # Fallback to simple iCal format
            ical_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Booking System//EN
BEGIN:VEVENT
UID:appointment-{appointment.id}@booking-system.com
DTSTAMP:{timezone.now().strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{appointment.start_date.strftime('%Y%m%dT%H%M%SZ')}
DTEND:{appointment.end_date.strftime('%Y%m%dT%H%M%SZ')}
SUMMARY:{appointment.service.title}
DESCRIPTION:{self.format_event_description(appointment, customer_appointment, request).replace(chr(10), '\\n')}
END:VEVENT
END:VCALENDAR"""
            return ical_content
    
    def update_event(self, appointment, event_id, customer_appointment=None, request=None):
        """Update Apple Calendar event (regenerate iCal)."""
        return {
            'success': True,
            'ical_file': self.generate_ical_file(appointment, customer_appointment, request),
        }
    
    def delete_event(self, event_id):
        """Delete Apple Calendar event (no-op for iCal files)."""
        return {
            'success': True,
        }
    
    def get_busy_times(self, start_date, end_date):
        """Get busy times from Apple Calendar (requires CalDAV server)."""
        # CalDAV implementation would go here
        # For now, return empty list
        return []


def get_calendar_service(staff):
    """
    Get appropriate calendar service instance for staff.
    
    Args:
        staff: Staff instance
    
    Returns:
        BaseCalendarService instance or None
    """
    if not staff or staff.calendar_provider == 'none':
        return None
    
    services = {
        'google': GoogleCalendarService,
        'outlook': OutlookCalendarService,
        'apple': AppleCalendarService,
    }
    
    service_class = services.get(staff.calendar_provider)
    if service_class:
        return service_class(staff)
    
    return None

