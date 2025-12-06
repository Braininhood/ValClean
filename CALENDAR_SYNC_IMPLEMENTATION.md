# Calendar Sync Implementation - Complete

## Overview

This document details the implementation of multi-calendar sync functionality for Google Calendar, Microsoft Outlook, and Apple Calendar integration.

## ✅ Completed Features

### 1. Calendar Services (`calendar_sync/services.py`)

**BaseCalendarService:**
- Abstract base class for all calendar providers
- Common methods: `authenticate`, `create_event`, `update_event`, `delete_event`, `get_busy_times`
- Event description formatting utility

**GoogleCalendarService:**
- OAuth 2.0 authentication
- Google Calendar API v3 integration
- Create/update/delete events
- Token refresh handling
- Busy times retrieval (two-way sync support)
- Calendar ID support (defaults to 'primary')

**OutlookCalendarService:**
- Microsoft Graph API OAuth 2.0 authentication
- Microsoft Graph Calendar API integration
- Create/update/delete events
- Token refresh handling
- Busy times retrieval (two-way sync support)
- Attendee support

**AppleCalendarService:**
- iCal file generation (.ics format)
- CalDAV support structure (ready for server setup)
- Download-ready calendar files
- Standard calendar app compatibility

**get_calendar_service() utility:**
- Factory function to get appropriate service instance
- Automatic provider selection based on staff settings

### 2. OAuth Views (`calendar_sync/views.py`)

**Google Calendar:**
- `connect_google_calendar` - Initiate OAuth flow
- `google_calendar_callback` - Handle OAuth callback and save tokens

**Microsoft Outlook:**
- `connect_outlook_calendar` - Initiate OAuth flow
- `outlook_calendar_callback` - Handle OAuth callback and save tokens

**General:**
- `disconnect_calendar` - Disconnect calendar from staff profile
- `download_ical` - Download iCal file for appointments (Apple Calendar)

### 3. Automatic Calendar Sync (`calendar_sync/signals.py`)

**Django Signals:**
- `sync_appointment_to_calendar` - Automatically syncs when appointment is created/updated
- `delete_appointment_from_calendar` - Automatically deletes calendar event when appointment is deleted

### 4. Integration with Appointment Creation

**Updated `appointments/views.py`:**
- Calendar sync integrated into `booking_step8_confirmation`
- Automatically creates calendar event when appointment is created
- Stores calendar event ID and provider in appointment record

### 5. URLs Configuration

**`calendar_sync/urls.py`:**
- `/calendar-sync/google/connect/` - Connect Google Calendar
- `/calendar-sync/google/callback/` - Google OAuth callback
- `/calendar-sync/outlook/connect/` - Connect Outlook Calendar
- `/calendar-sync/outlook/callback/` - Outlook OAuth callback
- `/calendar-sync/disconnect/` - Disconnect calendar
- `/calendar-sync/ical/<appointment_id>/` - Download iCal file

### 6. Settings Configuration

**Updated `config/settings.py`:**
```python
# Google Calendar
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default='')
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET', default='')
GOOGLE_REDIRECT_URI = config('GOOGLE_REDIRECT_URI', default='http://localhost:8000/calendar-sync/google/callback/')

# Microsoft Outlook Calendar
MICROSOFT_CLIENT_ID = config('MICROSOFT_CLIENT_ID', default='')
MICROSOFT_CLIENT_SECRET = config('MICROSOFT_CLIENT_SECRET', default='')
MICROSOFT_TENANT_ID = config('MICROSOFT_TENANT_ID', default='common')
MICROSOFT_REDIRECT_URI = config('MICROSOFT_REDIRECT_URI', default='http://localhost:8000/calendar-sync/outlook/callback/')
```

### 7. UI Integration

**Staff Dashboard:**
- Calendar connection section
- Connect/Disconnect buttons for Google and Outlook
- Connection status display
- Apple Calendar download instructions

**Appointment Confirmation:**
- Download iCal file button
- Works for all users (customer, staff, admin)

## 📋 Configuration Required

### Google Calendar Setup

**Step 1: Create Google Cloud Project**
1. Go to https://console.cloud.google.com
2. Create a new project or select existing
3. Enable **Google Calendar API**

**Step 2: Create OAuth 2.0 Credentials**
1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Application type: **Web application**
4. Authorized redirect URIs: `http://localhost:8000/calendar-sync/google/callback/` (development)
5. For production: `https://yourdomain.com/calendar-sync/google/callback/`
6. Copy **Client ID** and **Client Secret**

**Step 3: Add to `.env`**
```env
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/calendar-sync/google/callback/
```

### Microsoft Outlook Setup

**Step 1: Register App in Azure Portal**
1. Go to https://portal.azure.com
2. Go to **Azure Active Directory** → **App registrations**
3. Click **New registration**
4. Name: "Booking System Calendar"
5. Supported account types: **Accounts in any organizational directory and personal Microsoft accounts**
6. Redirect URI: `http://localhost:8000/calendar-sync/outlook/callback/` (Web)
7. Click **Register**

**Step 2: Configure API Permissions**
1. Go to **API permissions**
2. Click **Add a permission** → **Microsoft Graph** → **Delegated permissions**
3. Add: `Calendars.ReadWrite`, `offline_access`
4. Click **Add permissions**
5. Click **Grant admin consent** (if needed)

**Step 3: Get Credentials**
1. Go to **Certificates & secrets**
2. Click **New client secret**
3. Copy the **Value** (this is your client secret)
4. Go to **Overview**
5. Copy **Application (client) ID** and **Directory (tenant) ID**

**Step 4: Add to `.env`**
```env
MICROSOFT_CLIENT_ID=your_application_client_id
MICROSOFT_CLIENT_SECRET=your_client_secret_value
MICROSOFT_TENANT_ID=your_tenant_id_or_common
MICROSOFT_REDIRECT_URI=http://localhost:8000/calendar-sync/outlook/callback/
```

### Apple Calendar

**No API keys needed!** Apple Calendar uses iCal file downloads:
- iCal files are generated automatically
- Users download and import to their calendar app
- Works with Apple Calendar, Google Calendar, Outlook, Thunderbird, etc.

## 🚀 Usage

### For Staff Members

1. **Connect Calendar:**
   - Go to Staff Dashboard
   - Click "Connect Google Calendar" or "Connect Outlook"
   - Authorize the application
   - Calendar will be automatically connected

2. **Automatic Sync:**
   - When appointments are created, they automatically sync to your calendar
   - When appointments are updated, calendar events are updated
   - When appointments are deleted, calendar events are deleted

3. **Disconnect:**
   - Click "Disconnect Calendar" in Staff Dashboard
   - Calendar sync will stop

### For Customers

1. **Download iCal File:**
   - After booking, click "Add to Calendar (iCal)" on confirmation page
   - Or go to appointment details and download iCal file
   - Import into your calendar app

### For Administrators

- View calendar sync status in Staff admin
- See which staff members have calendars connected
- Monitor calendar sync errors in logs

## 🔧 How It Works

### Automatic Sync Flow

1. **Appointment Created:**
   - Django signal triggers `sync_appointment_to_calendar`
   - Calendar service creates event in provider calendar
   - Event ID stored in appointment record

2. **Appointment Updated:**
   - Django signal triggers `sync_appointment_to_calendar`
   - Calendar service updates existing event
   - Event details updated in provider calendar

3. **Appointment Deleted:**
   - Django signal triggers `delete_appointment_from_calendar`
   - Calendar service deletes event from provider calendar

### Token Management

- **Access Tokens:** Stored in `staff.calendar_data`
- **Refresh Tokens:** Stored for offline access
- **Token Expiry:** Automatically refreshed when expired
- **Token Security:** Stored in database (consider encryption for production)

## 📝 Notes

- **Google Calendar:** Requires OAuth 2.0 credentials
- **Microsoft Outlook:** Requires Azure AD app registration
- **Apple Calendar:** No API keys needed (iCal download)
- **Token Refresh:** Automatic for Google and Outlook
- **Error Handling:** Failures are logged but don't block appointment creation
- **Two-Way Sync:** Busy times retrieval implemented (can be used for availability checking)

## ✅ Testing Checklist

- [x] Calendar service classes created
- [x] OAuth views implemented
- [x] Django signals for automatic sync
- [x] Appointment creation integration
- [x] iCal file generation
- [x] Staff dashboard UI
- [x] Settings configuration
- [x] URLs configured
- [ ] **Google OAuth credentials need to be added** (user action required)
- [ ] **Microsoft OAuth credentials need to be added** (user action required)
- [ ] **Test Google Calendar connection** (after credentials added)
- [ ] **Test Outlook Calendar connection** (after credentials added)
- [ ] **Test iCal download** (works immediately)
- [ ] **Test automatic sync on appointment creation** (after credentials added)

## 🔄 Next Steps

1. **Get OAuth Credentials:**
   - Set up Google Cloud project and get credentials
   - Set up Azure AD app and get credentials

2. **Add to `.env` file:**
   - Add all calendar OAuth credentials
   - Update redirect URIs for production domain

3. **Test Connections:**
   - Connect Google Calendar from staff dashboard
   - Connect Outlook Calendar from staff dashboard
   - Test appointment creation and verify calendar sync

4. **Production Setup:**
   - Update redirect URIs to production domain
   - Consider token encryption for production
   - Set up monitoring for calendar sync errors

---

**Status**: ✅ Calendar Sync Implementation Complete (OAuth Credentials Required)
**Last Updated**: December 2025

