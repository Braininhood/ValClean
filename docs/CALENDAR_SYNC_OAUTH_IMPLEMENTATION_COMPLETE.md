# Calendar Sync OAuth Implementation - COMPLETE ✅

## 🎉 Implementation Summary

All three requested features have been implemented:

1. ✅ **OAuth 2.0 for Google Calendar** - Complete
2. ✅ **OAuth 2.0 for Microsoft Outlook** - Complete
3. ✅ **.ics file download endpoint for Apple Calendar** - Complete

---

## 📋 What Was Implemented

### 1. Google Calendar OAuth 2.0 ✓

**Files Modified:**
- `backend/apps/calendar_sync/views.py` - OAuth views added
- `backend/apps/calendar_sync/services.py` - Google Calendar API calls implemented
- `backend/apps/calendar_sync/urls.py` - URL routes added

**Endpoints Created:**
- `POST /api/calendar/google/connect/` - Start OAuth flow
- `GET /api/calendar/google/callback/` - Handle OAuth callback
- `POST /api/calendar/google/disconnect/` - Disconnect Google Calendar

**Features:**
- OAuth 2.0 authorization flow
- Token storage in `Profile` model
- Token refresh handling
- Google Calendar API integration:
  - Create events
  - Update events
  - Delete events

**Required Settings (add to `.env` or `settings.py`):**
```python
GOOGLE_CLIENT_ID = 'your-google-client-id'
GOOGLE_CLIENT_SECRET = 'your-google-client-secret'
GOOGLE_REDIRECT_URI = 'http://localhost:8000/api/calendar/google/callback/'
```

**Required Libraries:**
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

---

### 2. Microsoft Outlook OAuth 2.0 ✓

**Files Modified:**
- `backend/apps/calendar_sync/views.py` - OAuth views added
- `backend/apps/calendar_sync/services.py` - Microsoft Graph API calls implemented
- `backend/apps/calendar_sync/urls.py` - URL routes added

**Endpoints Created:**
- `POST /api/calendar/outlook/connect/` - Start OAuth flow
- `GET /api/calendar/outlook/callback/` - Handle OAuth callback
- `POST /api/calendar/outlook/disconnect/` - Disconnect Outlook

**Features:**
- OAuth 2.0 authorization flow (MSAL)
- Token storage in `Profile` model
- Microsoft Graph API integration:
  - Create events
  - Update events
  - Delete events

**Required Settings (add to `.env` or `settings.py`):**
```python
OUTLOOK_CLIENT_ID = 'your-outlook-client-id'
OUTLOOK_CLIENT_SECRET = 'your-outlook-client-secret'
OUTLOOK_REDIRECT_URI = 'http://localhost:8000/api/calendar/outlook/callback/'
```

**Required Libraries:**
```bash
pip install msal msgraph-sdk requests
```

---

### 3. Apple Calendar .ics File Download ✓

**Files Modified:**
- `backend/apps/calendar_sync/views.py` - .ics download view added
- `backend/apps/calendar_sync/services.py` - .ics generation already implemented
- `backend/apps/calendar_sync/urls.py` - URL route added

**Endpoint Created:**
- `GET /api/calendar/ics/<appointment_id>/` - Download .ics file

**Features:**
- Generates .ics file for any appointment
- Role-based access control (customer/staff/manager/admin)
- Event data tailored by user role
- Direct file download response

**Usage:**
```
GET /api/calendar/ics/123/
Authorization: Bearer <jwt_token>
```

Returns `.ics` file that can be imported into:
- Apple Calendar
- Google Calendar (via import)
- Microsoft Outlook (via import)
- Any calendar app supporting .ics format

---

## 🔧 How to Use

### Google Calendar Setup:

1. **Get Google OAuth Credentials:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a project
   - Enable Google Calendar API
   - Create OAuth 2.0 credentials
   - Add redirect URI: `http://localhost:8000/api/calendar/google/callback/`

2. **Add to `.env` file:**
   ```bash
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   GOOGLE_REDIRECT_URI=http://localhost:8000/api/calendar/google/callback/
   ```

3. **Install libraries:**
   ```bash
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```

4. **Connect Calendar:**
   ```bash
   POST /api/calendar/google/connect/
   Authorization: Bearer <jwt_token>
   ```
   Returns `authorization_url` - redirect user to this URL

5. **After OAuth callback:**
   - User is redirected back to frontend
   - Tokens stored in `Profile` model
   - Calendar sync enabled automatically

### Microsoft Outlook Setup:

1. **Get Microsoft Azure App Credentials:**
   - Go to [Azure Portal](https://portal.azure.com/)
   - Register an app
   - Add redirect URI: `http://localhost:8000/api/calendar/outlook/callback/`
   - Grant "Calendars.ReadWrite" permission

2. **Add to `.env` file:**
   ```bash
   OUTLOOK_CLIENT_ID=your-client-id
   OUTLOOK_CLIENT_SECRET=your-client-secret
   OUTLOOK_REDIRECT_URI=http://localhost:8000/api/calendar/outlook/callback/
   ```

3. **Install libraries:**
   ```bash
   pip install msal requests
   ```

4. **Connect Calendar:**
   ```bash
   POST /api/calendar/outlook/connect/
   Authorization: Bearer <jwt_token>
   ```
   Returns `authorization_url` - redirect user to this URL

### Apple Calendar (.ics) Usage:

1. **Download .ics file:**
   ```bash
   GET /api/calendar/ics/<appointment_id>/
   Authorization: Bearer <jwt_token>
   ```

2. **Frontend can:**
   - Download file directly
   - Email file to user
   - Save file to server and provide download link

---

## 📁 File Structure

```
backend/apps/calendar_sync/
├── views.py          # OAuth views + .ics download view (NEW/COMPLETE)
├── services.py       # Calendar API integration (UPDATED/COMPLETE)
├── urls.py           # URL routes (UPDATED/COMPLETE)
├── models.py         # Placeholder (not needed - using Profile/Appointment)
├── serializers.py    # Placeholder
└── admin.py          # Placeholder
```

---

## 🔄 Integration with Order Confirmation

When an order is confirmed:

1. **Appointments created** (via signals in `apps/orders/signals.py`)
2. **Calendar sync triggered** (for users with `calendar_sync_enabled=True`)
3. **Events created automatically**:
   - Google Calendar: Event created via API
   - Outlook: Event created via Microsoft Graph API
   - Apple Calendar: .ics file generated (user can download)

---

## 🧪 Testing

### Test Google Calendar:

1. Connect Google Calendar:
   ```bash
   curl -X POST http://localhost:8000/api/calendar/google/connect/ \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json"
   ```

2. Confirm an order (triggers appointment creation)
3. Check `appointment.calendar_event_id['google']` - should have event ID
4. Check Google Calendar - event should appear

### Test Outlook:

1. Connect Outlook:
   ```bash
   curl -X POST http://localhost:8000/api/calendar/outlook/connect/ \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json"
   ```

2. Confirm an order (triggers appointment creation)
3. Check `appointment.calendar_event_id['outlook']` - should have event ID
4. Check Outlook Calendar - event should appear

### Test .ics Download:

```bash
curl -X GET http://localhost:8000/api/calendar/ics/123/ \
  -H "Authorization: Bearer <token>" \
  --output appointment.ics
```

Open `appointment.ics` in calendar app - should import successfully.

---

## ⚠️ Important Notes

1. **OAuth Credentials Required:**
   - Google and Outlook require OAuth credentials from their respective platforms
   - These are NOT included in the codebase (security best practice)

2. **Libraries Optional:**
   - Code handles missing libraries gracefully
   - If libraries not installed, API returns `503 Service Unavailable`
   - Install libraries to enable full functionality

3. **Token Security:**
   - Tokens stored in `Profile` model (should be encrypted in production)
   - Consider using Django's `encrypted_fields` or similar for production

4. **Redirect URIs:**
   - Must match exactly in OAuth provider configuration
   - Update `GOOGLE_REDIRECT_URI` and `OUTLOOK_REDIRECT_URI` in settings

---

## ✅ Status

**All features implemented and ready for testing!**

- ✅ Google Calendar OAuth 2.0 flow
- ✅ Google Calendar API (create/update/delete events)
- ✅ Microsoft Outlook OAuth 2.0 flow
- ✅ Microsoft Graph API (create/update/delete events)
- ✅ Apple Calendar .ics file generation and download

**Next Steps:**
1. Get OAuth credentials from Google and Microsoft
2. Add credentials to `.env` file
3. Install required libraries
4. Test OAuth flows
5. Confirm an order to test automatic calendar sync
