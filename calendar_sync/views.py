"""
Calendar sync views for OAuth authentication and calendar management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from datetime import timedelta
import urllib.parse

from staff.models import Staff
from .services import get_calendar_service, GoogleCalendarService, OutlookCalendarService


@login_required
def connect_google_calendar(request):
    """Initiate Google Calendar OAuth connection."""
    try:
        staff = Staff.objects.get(user=request.user)
    except Staff.DoesNotExist:
        messages.error(request, 'Staff profile not found.')
        return redirect('staff:staff_dashboard')
    
    client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '')
    redirect_uri = getattr(settings, 'GOOGLE_REDIRECT_URI', '')
    
    if not client_id or not redirect_uri:
        messages.error(request, 'Google Calendar is not configured. Please contact administrator.')
        return redirect('staff:staff_dashboard')
    
    # Build OAuth URL
    scope = 'https://www.googleapis.com/auth/calendar'
    state = f"staff_{staff.id}"
    
    oauth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}&"
        f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
        f"response_type=code&"
        f"scope={urllib.parse.quote(scope)}&"
        f"access_type=offline&"
        f"prompt=consent&"
        f"state={state}"
    )
    
    return redirect(oauth_url)


@login_required
def google_calendar_callback(request):
    """Handle Google Calendar OAuth callback."""
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')
    
    if error:
        messages.error(request, f'Google Calendar connection failed: {error}')
        return redirect('staff:staff_dashboard')
    
    if not code or not state:
        messages.error(request, 'Invalid callback parameters.')
        return redirect('staff:staff_dashboard')
    
    # Extract staff ID from state
    try:
        staff_id = int(state.replace('staff_', ''))
        staff = Staff.objects.get(id=staff_id, user=request.user)
    except (ValueError, Staff.DoesNotExist):
        messages.error(request, 'Invalid staff profile.')
        return redirect('staff:staff_dashboard')
    
    # Exchange code for tokens
    client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '')
    client_secret = getattr(settings, 'GOOGLE_CLIENT_SECRET', '')
    redirect_uri = getattr(settings, 'GOOGLE_REDIRECT_URI', '')
    
    try:
        import requests
        
        token_url = 'https://oauth2.googleapis.com/token'
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
        }
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        
        # Save tokens to staff calendar_data
        calendar_data = staff.calendar_data or {}
        calendar_data['access_token'] = token_data['access_token']
        calendar_data['refresh_token'] = token_data.get('refresh_token', '')
        calendar_data['expires_at'] = (
            timezone.now() + timedelta(seconds=token_data.get('expires_in', 3600))
        ).isoformat()
        
        staff.calendar_data = calendar_data
        staff.calendar_provider = 'google'
        staff.calendar_id = 'primary'  # Default to primary calendar
        staff.save()
        
        messages.success(request, 'Google Calendar connected successfully!')
        
    except Exception as e:
        messages.error(request, f'Error connecting Google Calendar: {str(e)}')
    
    return redirect('staff:staff_dashboard')


@login_required
def connect_outlook_calendar(request):
    """Initiate Microsoft Outlook Calendar OAuth connection."""
    try:
        staff = Staff.objects.get(user=request.user)
    except Staff.DoesNotExist:
        messages.error(request, 'Staff profile not found.')
        return redirect('staff:staff_dashboard')
    
    client_id = getattr(settings, 'MICROSOFT_CLIENT_ID', '')
    redirect_uri = getattr(settings, 'MICROSOFT_REDIRECT_URI', '')
    tenant_id = getattr(settings, 'MICROSOFT_TENANT_ID', 'common')
    
    if not client_id or not redirect_uri:
        messages.error(request, 'Microsoft Outlook is not configured. Please contact administrator.')
        return redirect('staff:staff_dashboard')
    
    # Build OAuth URL
    scope = 'https://graph.microsoft.com/Calendars.ReadWrite offline_access'
    state = f"staff_{staff.id}"
    
    oauth_url = (
        f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize?"
        f"client_id={client_id}&"
        f"response_type=code&"
        f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
        f"response_mode=query&"
        f"scope={urllib.parse.quote(scope)}&"
        f"state={state}"
    )
    
    return redirect(oauth_url)


@login_required
def outlook_calendar_callback(request):
    """Handle Microsoft Outlook Calendar OAuth callback."""
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')
    
    if error:
        messages.error(request, f'Microsoft Outlook connection failed: {error}')
        return redirect('staff:staff_dashboard')
    
    if not code or not state:
        messages.error(request, 'Invalid callback parameters.')
        return redirect('staff:staff_dashboard')
    
    # Extract staff ID from state
    try:
        staff_id = int(state.replace('staff_', ''))
        staff = Staff.objects.get(id=staff_id, user=request.user)
    except (ValueError, Staff.DoesNotExist):
        messages.error(request, 'Invalid staff profile.')
        return redirect('staff:staff_dashboard')
    
    # Exchange code for tokens
    client_id = getattr(settings, 'MICROSOFT_CLIENT_ID', '')
    client_secret = getattr(settings, 'MICROSOFT_CLIENT_SECRET', '')
    redirect_uri = getattr(settings, 'MICROSOFT_REDIRECT_URI', '')
    tenant_id = getattr(settings, 'MICROSOFT_TENANT_ID', 'common')
    
    try:
        import requests
        
        token_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
            'scope': 'https://graph.microsoft.com/Calendars.ReadWrite offline_access',
        }
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        
        # Save tokens to staff calendar_data
        calendar_data = staff.calendar_data or {}
        calendar_data['access_token'] = token_data['access_token']
        calendar_data['refresh_token'] = token_data.get('refresh_token', '')
        calendar_data['expires_at'] = (
            timezone.now() + timedelta(seconds=token_data.get('expires_in', 3600))
        ).isoformat()
        
        staff.calendar_data = calendar_data
        staff.calendar_provider = 'outlook'
        staff.save()
        
        messages.success(request, 'Microsoft Outlook Calendar connected successfully!')
        
    except Exception as e:
        messages.error(request, f'Error connecting Microsoft Outlook: {str(e)}')
    
    return redirect('staff:staff_dashboard')


@login_required
def disconnect_calendar(request):
    """Disconnect calendar from staff profile."""
    try:
        staff = Staff.objects.get(user=request.user)
    except Staff.DoesNotExist:
        messages.error(request, 'Staff profile not found.')
        return redirect('staff:staff_dashboard')
    
    staff.calendar_provider = 'none'
    staff.calendar_id = ''
    staff.calendar_data = {}
    staff.save()
    
    messages.success(request, 'Calendar disconnected successfully.')
    return redirect('staff:staff_dashboard')


@login_required
def download_ical(request, appointment_id):
    """Download iCal file for appointment (Apple Calendar)."""
    from appointments.models import Appointment
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permissions
    if not request.user.is_superuser and request.user.role != 'admin':
        if request.user.role == 'staff':
            try:
                staff = Staff.objects.get(user=request.user)
                if appointment.staff != staff:
                    messages.error(request, 'You do not have permission to download this calendar file.')
                    return redirect('staff:staff_dashboard')
            except Staff.DoesNotExist:
                messages.error(request, 'Staff profile not found.')
                return redirect('staff:staff_dashboard')
        elif request.user.role == 'customer':
            from customers.models import Customer
            try:
                customer = Customer.objects.get(user=request.user)
                customer_appointment = appointment.customer_appointments.filter(customer=customer).first()
                if not customer_appointment:
                    messages.error(request, 'You do not have permission to download this calendar file.')
                    return redirect('customers:customer_dashboard')
            except Customer.DoesNotExist:
                messages.error(request, 'Customer profile not found.')
                return redirect('customers:customer_dashboard')
    
    # Generate iCal file
    from .services import AppleCalendarService
    
    customer_appointment = appointment.customer_appointments.first()
    apple_service = AppleCalendarService(appointment.staff)
    ical_content = apple_service.generate_ical_file(appointment, customer_appointment, request)
    
    # Create response
    response = HttpResponse(ical_content, content_type='text/calendar')
    response['Content-Disposition'] = f'attachment; filename="appointment-{appointment.id}.ics"'
    
    return response
