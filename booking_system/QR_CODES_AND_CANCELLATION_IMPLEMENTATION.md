# QR Codes, Calendar Links, and Cancellation System Implementation

**Date**: December 2025  
**Status**: ✅ Complete

## Overview

This document details the implementation of QR code generation, calendar integration links, and the enhanced appointment cancellation system. These features improve user experience by providing quick access to appointment details and easy cancellation options.

---

## 1. QR Code Generation

### 1.1 Implementation Details

**File**: `core/utils.py`

Added QR code generation functionality for appointments:

- **Function**: `generate_qr_code(data, size=200)`
  - Generates QR code images using the `qrcode` library
  - Returns a BytesIO buffer containing the PNG image
  - Configurable size (default: 200x200 pixels)

- **Function**: `generate_appointment_qr_code(appointment, customer_appointment=None, request=None)`
  - Generates QR codes specifically for appointments
  - Includes appointment details (booking #, service, staff, date, duration, status)
  - Contains a link to view appointment details using token
  - Uses correct domain from request or Sites framework

### 1.2 Features

- **Appointment Details**: QR code contains all relevant appointment information
- **Token-Based Access**: QR codes link to public appointment view using unique tokens
- **Domain Handling**: Automatically uses correct domain (localhost in dev, production domain in prod)
- **Error Handling**: Graceful fallback if QR code generation fails

### 1.3 Usage

QR codes are displayed on:
- Booking confirmation page (`booking_step8_confirmation.html`)
- Can be scanned to quickly access appointment details
- Embedded as base64-encoded images in templates

---

## 2. Appointment Links System

### 2.1 Implementation Details

**File**: `core/utils.py`

Added comprehensive link generation for appointments:

- **Function**: `get_appointment_links(appointment, customer_appointment=None, request=None)`
  - Returns dictionary with all relevant appointment links
  - Includes: view, cancel, iCal download, Google Calendar, Outlook Calendar
  - Handles domain resolution correctly

### 2.2 Link Types

1. **View Links**:
   - `/appointments/{id}/` - Authenticated view
   - `/appointments/view/{token}/` - Public token-based view

2. **Cancel Link**:
   - `/appointments/cancel/{token}/` - Public cancellation page

3. **Calendar Links**:
   - `/calendar-sync/ical/{id}/` - iCal file download
   - Google Calendar direct add link (pre-filled event)
   - Outlook Calendar direct add link (pre-filled event)

### 2.3 Google Calendar Integration

**Fixed Issues**:
- **Timezone Error**: Fixed `AttributeError: module 'django.utils.timezone' has no attribute 'utc'`
  - Solution: Use `from datetime import timezone as dt_timezone` and `dt_timezone.utc`
- **URL Generation**: Properly formats dates in UTC (YYYYMMDDTHHMMSSZ format)
- **Error Handling**: Multiple fallback levels to ensure URL is always generated

**URL Format**:
```
https://calendar.google.com/calendar/render?
  action=TEMPLATE&
  text={title}&
  dates={start_utc}/{end_utc}&
  details={details}&
  location={location}
```

### 2.4 Outlook Calendar Integration

**URL Format**:
```
https://outlook.live.com/calendar/0/deeplink/compose?
  subject={title}&
  startdt={start_iso}&
  enddt={end_iso}&
  body={body}&
  location={location}
```

---

## 3. Domain Handling Fixes

### 3.1 Problem

QR codes and links were using `example.com` instead of `localhost:8000` in development.

### 3.2 Solution

**Multiple Fixes Applied**:

1. **Sites Framework Integration**:
   - Added `django.contrib.sites` to `INSTALLED_APPS`
   - Set `SITE_ID = 1` in settings
   - Updated Site domain to `localhost:8000` via management command

2. **URL Generation Priority**:
   - **First**: Use `request.get_host()` if request is available (most accurate)
   - **Second**: Use Sites framework domain
   - **Third**: Fallback to `settings.DOMAIN` or `localhost:8000`

3. **Files Updated**:
   - `core/utils.py` - Both QR code and link generation functions
   - `calendar_sync/services.py` - Calendar event descriptions
   - `config/settings.py` - Sites framework configuration

### 3.3 Code Pattern

```python
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
```

---

## 4. Appointment Cancellation System

### 4.1 Previous Behavior

- Only allowed cancellation for "approved" appointments
- Changed status to "cancelled" but didn't delete
- Showed error messages for other statuses

### 4.2 New Behavior

**File**: `appointments/views.py` - `cancel_appointment_by_token()`

**Changes**:
1. **Removed Status Restrictions**: Users can cancel appointments with ANY status
2. **Deletion Logic**: 
   - Deletes `CustomerAppointment` (removes from all dashboards)
   - If it's the only customer for the appointment, also deletes the `Appointment`
3. **Calendar Sync**: Automatically handled via `pre_delete` signal
4. **Redirect Logic**: Redirects to customer dashboard if logged in, otherwise home

### 4.3 Implementation Details

```python
if request.method == 'POST':
    # Check for other customer appointments
    other_customer_appointments = CustomerAppointment.objects.filter(
        appointment=appointment
    ).exclude(id=customer_appointment.id)
    
    # Delete the CustomerAppointment
    customer_appointment.delete()
    
    # If no other CustomerAppointments exist, delete the Appointment too
    if not other_customer_appointments.exists():
        appointment.delete()
        messages.success(request, 'Your appointment has been cancelled and deleted successfully.')
    else:
        messages.success(request, 'Your appointment has been cancelled successfully.')
```

### 4.4 Template Updates

**File**: `templates/appointments/cancel_appointment.html`

**Changes**:
- Removed status-based restrictions
- Simplified to show only confirmation question
- Always shows "Yes, Cancel Appointment" and "No, Keep Appointment" buttons
- Removed conditional logic that prevented cancellation

---

## 5. Public Appointment Views

### 5.1 Token-Based Access

**New Views**:
- `view_appointment_by_token(request, token)` - Public appointment details
- `cancel_appointment_by_token(request, token)` - Public cancellation

**URL Patterns**:
```python
path('view/<str:token>/', views.view_appointment_by_token, name='view_appointment_by_token'),
path('cancel/<str:token>/', views.cancel_appointment_by_token, name='cancel_appointment_by_token'),
```

### 5.2 Templates

- `templates/appointments/view_appointment.html` - Public appointment details view
- `templates/appointments/cancel_appointment.html` - Simplified cancellation confirmation

---

## 6. Confirmation Page Enhancements

### 6.1 New Sections

**File**: `templates/appointments/booking_step8_confirmation.html`

**Added**:

1. **QR Code Section**:
   - Displays QR code as base64-encoded image
   - Includes instructions for scanning
   - Max size: 200x200 pixels

2. **Calendar Links Section**:
   - Download iCal button
   - Add to Google Calendar button (always visible, disabled if link unavailable)
   - Add to Outlook Calendar button (always visible, disabled if link unavailable)

3. **Quick Links Section**:
   - View Details button (token-based public link)
   - Cancel Appointment button (token-based public link)

### 6.2 Button States

- **Active**: When link is successfully generated
- **Disabled**: When link generation fails (with tooltip explaining why)

---

## 7. Calendar Sync Integration

### 7.1 Event Descriptions

**File**: `calendar_sync/services.py`

**Updated**: `format_event_description()` method

**Changes**:
- Now accepts optional `request` parameter for URL generation
- Includes appointment links in calendar event descriptions:
  - View Appointment link
  - Download Calendar link
  - View Details link (token-based)
  - Cancel Appointment link (token-based)

### 7.2 Service Updates

All calendar services updated to pass `request` parameter:
- `GoogleCalendarService.create_event()`
- `OutlookCalendarService.create_event()`
- `AppleCalendarService.generate_ical_file()`

---

## 8. Dependencies Added

### 8.1 New Packages

**File**: `requirements.txt`

```python
qrcode>=7.4.2  # QR code generation
Pillow>=10.0.0  # Required by qrcode
```

### 8.2 Django Apps

**File**: `config/settings.py`

```python
INSTALLED_APPS = [
    # ...
    'django.contrib.sites',  # For Site framework (used in QR codes and links)
    # ...
]

SITE_ID = 1  # Required for django.contrib.sites
```

---

## 9. Testing and Verification

### 9.1 System Checks

All changes pass Django system checks:
```bash
python manage.py check
# System check identified no issues (0 silenced).
```

### 9.2 Manual Testing Checklist

- [x] QR code generates correctly on confirmation page
- [x] QR code contains correct appointment details
- [x] QR code links to correct domain (localhost in dev)
- [x] Google Calendar button is active and functional
- [x] Outlook Calendar button is active and functional
- [x] View Details link works with token
- [x] Cancel Appointment link works with token
- [x] Cancellation works for all appointment statuses
- [x] Cancelled appointments are removed from dashboards
- [x] Calendar events are deleted when appointments are cancelled
- [x] All links use correct domain (not example.com)

---

## 10. Files Modified

### 10.1 Core Files

1. **`core/utils.py`**
   - Added `generate_qr_code()` function
   - Added `generate_appointment_qr_code()` function
   - Added `get_appointment_links()` function
   - Fixed timezone handling for Google Calendar URLs
   - Fixed domain resolution logic

2. **`appointments/views.py`**
   - Updated `booking_step8_confirmation()` to generate QR codes and links
   - Added `view_appointment_by_token()` view
   - Updated `cancel_appointment_by_token()` to delete appointments
   - Removed status restrictions from cancellation

3. **`appointments/urls.py`**
   - Added URL patterns for token-based views

4. **`config/settings.py`**
   - Added `django.contrib.sites` to INSTALLED_APPS
   - Added `SITE_ID = 1`

### 10.2 Templates

1. **`templates/appointments/booking_step8_confirmation.html`**
   - Added QR code section
   - Added calendar links section
   - Added quick links section
   - Updated button states

2. **`templates/appointments/cancel_appointment.html`**
   - Removed status restrictions
   - Simplified confirmation page
   - Always shows cancellation form

3. **`templates/appointments/view_appointment.html`**
   - New template for public appointment viewing

### 10.3 Calendar Sync

1. **`calendar_sync/services.py`**
   - Updated `format_event_description()` to accept request parameter
   - Updated all calendar services to pass request parameter
   - Added links to calendar event descriptions

2. **`calendar_sync/views.py`**
   - Updated `download_ical()` to pass request parameter

---

## 11. Migration Requirements

### 11.1 Sites Framework

Run the following command to set up Sites framework:

```bash
python manage.py migrate sites
python manage.py shell -c "from django.contrib.sites.models import Site; site = Site.objects.get(pk=1); site.domain = 'localhost:8000'; site.name = 'Local Development'; site.save()"
```

For production, update the domain:
```bash
python manage.py shell -c "from django.contrib.sites.models import Site; site = Site.objects.get(pk=1); site.domain = 'yourdomain.com'; site.name = 'Your Site Name'; site.save()"
```

---

## 12. Known Issues and Solutions

### 12.1 Timezone Issue (Fixed)

**Problem**: `AttributeError: module 'django.utils.timezone' has no attribute 'utc'`

**Solution**: Use Python's `datetime.timezone.utc` instead:
```python
from datetime import timezone as dt_timezone
start_utc = start_utc.astimezone(dt_timezone.utc)
```

### 12.2 Domain Issue (Fixed)

**Problem**: QR codes and links using `example.com` instead of `localhost:8000`

**Solution**: 
1. Added Sites framework
2. Updated domain resolution logic to prioritize `request.get_host()`
3. Updated Site domain in database

---

## 13. Future Enhancements

### 13.1 Potential Improvements

1. **QR Code Customization**:
   - Custom QR code colors
   - Logo embedding in QR codes
   - Different QR code sizes

2. **Additional Calendar Providers**:
   - Apple Calendar direct links (currently iCal only)
   - Yahoo Calendar support
   - Other calendar providers

3. **Cancellation Notifications**:
   - Email notifications when appointments are cancelled
   - SMS notifications for cancellations
   - Staff notifications for cancellations

4. **Analytics**:
   - Track QR code scans
   - Track calendar link clicks
   - Track cancellation rates

---

## 14. Summary

### 14.1 Completed Features

✅ QR code generation for appointments  
✅ Comprehensive appointment links system  
✅ Google Calendar direct add links  
✅ Outlook Calendar direct add links  
✅ Token-based public appointment views  
✅ Enhanced cancellation system (any status, deletion)  
✅ Domain handling fixes (localhost in dev)  
✅ Calendar event descriptions with links  
✅ Sites framework integration  

### 14.2 Benefits

1. **User Experience**: Quick access to appointment details via QR codes
2. **Convenience**: One-click calendar integration
3. **Flexibility**: Cancel appointments at any time, regardless of status
4. **Clean Data**: Deleted appointments removed from all dashboards
5. **Public Access**: Token-based links work without authentication

---

**Last Updated**: December 2025  
**Status**: ✅ All features implemented and tested

