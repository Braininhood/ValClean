# Calendar Sync Configuration Guide

This guide provides step-by-step instructions for configuring Google Calendar, Microsoft Outlook, and Apple Calendar integration.

---

## 📅 Google Calendar Configuration

### Step 1: Create Google Cloud Project

1. Go to https://console.cloud.google.com
2. Click **Select a project** → **New Project**
3. Enter project name: "Booking System Calendar"
4. Click **Create**
5. Wait for project creation (may take a few seconds)

### Step 2: Enable Google Calendar API

1. In Google Cloud Console, go to **APIs & Services** → **Library**
2. Search for "Google Calendar API"
3. Click on **Google Calendar API**
4. Click **Enable**
5. Wait for API to be enabled

### Step 3: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
3. If prompted, configure OAuth consent screen first:
   - **User Type:** External (or Internal if using Google Workspace)
   - Click **Create**
   - **App name:** Booking System
   - **User support email:** Your email
   - **Developer contact:** Your email
   - Click **Save and Continue**
   - **Scopes:** Click **Add or Remove Scopes**
     - Search and add: `.../auth/calendar`
     - Click **Update** → **Save and Continue**
   - **Test users:** Add your email (for testing)
   - Click **Save and Continue** → **Back to Dashboard**

4. Now create OAuth client ID:
   - **Application type:** Web application
   - **Name:** Booking System Web Client
   - **Authorized JavaScript origins:** 
     - `http://localhost:8000` (development)
     - `https://yourdomain.com` (production)
   - **Authorized redirect URIs:**
     - `http://localhost:8000/calendar-sync/google/callback/` (development)
     - `https://yourdomain.com/calendar-sync/google/callback/` (production)
   - Click **Create**

5. **Copy the credentials:**
   - **Client ID:** (starts with something like `123456789-abc...apps.googleusercontent.com`)
   - **Client Secret:** (long string)
   - **Save these securely!**

### Step 4: Add to `.env` File

```env
GOOGLE_CLIENT_ID=123456789-abc123def456.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/calendar-sync/google/callback/
```

**For Production:**
```env
GOOGLE_REDIRECT_URI=https://yourdomain.com/calendar-sync/google/callback/
```

### Step 5: Testing

1. Start Django server: `python manage.py runserver`
2. Log in as a staff member
3. Go to Staff Dashboard
4. Click "Connect Google Calendar"
5. Authorize the application
6. You should be redirected back and see "Google Calendar connected successfully!"

---

## 📧 Microsoft Outlook Calendar Configuration

### Step 1: Register App in Azure Portal

1. Go to https://portal.azure.com
2. Sign in with your Microsoft account
3. Go to **Azure Active Directory** (or search for it)
4. Click **App registrations** in the left menu
5. Click **+ New registration**

### Step 2: Configure App Registration

1. **Name:** Booking System Calendar
2. **Supported account types:** 
   - Select: **Accounts in any organizational directory and personal Microsoft accounts**
3. **Redirect URI:**
   - Platform: **Web**
   - URI: `http://localhost:8000/calendar-sync/outlook/callback/`
4. Click **Register**

### Step 3: Configure API Permissions

1. In your app registration, go to **API permissions**
2. Click **+ Add a permission**
3. Select **Microsoft Graph**
4. Select **Delegated permissions**
5. Search and add:
   - `Calendars.ReadWrite` - Read and write calendars
   - `offline_access` - Maintain access to data (for refresh tokens)
6. Click **Add permissions**

### Step 4: Grant Admin Consent (Optional)

1. Click **Grant admin consent for [Your Organization]**
2. Click **Yes** to confirm
3. This allows all users in your organization to use the app

**Note:** For personal Microsoft accounts, users will consent individually.

### Step 5: Create Client Secret

1. Go to **Certificates & secrets**
2. Click **+ New client secret**
3. **Description:** Booking System Secret
4. **Expires:** Choose expiration (24 months recommended)
5. Click **Add**
6. **IMPORTANT:** Copy the **Value** immediately (you won't see it again!)
   - This is your `MICROSOFT_CLIENT_SECRET`

### Step 6: Get Application Details

1. Go to **Overview** in your app registration
2. Copy:
   - **Application (client) ID** → This is `MICROSOFT_CLIENT_ID`
   - **Directory (tenant) ID** → This is `MICROSOFT_TENANT_ID`
   - For personal accounts, use `common` as tenant ID

### Step 7: Add to `.env` File

```env
MICROSOFT_CLIENT_ID=12345678-1234-1234-1234-123456789abc
MICROSOFT_CLIENT_SECRET=your_client_secret_value_here
MICROSOFT_TENANT_ID=common
MICROSOFT_REDIRECT_URI=http://localhost:8000/calendar-sync/outlook/callback/
```

**For Production:**
```env
MICROSOFT_REDIRECT_URI=https://yourdomain.com/calendar-sync/outlook/callback/
```

**For Organization (Single Tenant):**
```env
MICROSOFT_TENANT_ID=your_tenant_id_here
```

### Step 8: Testing

1. Start Django server: `python manage.py runserver`
2. Log in as a staff member
3. Go to Staff Dashboard
4. Click "Connect Outlook"
5. Sign in with Microsoft account
6. Authorize the application
7. You should be redirected back and see "Microsoft Outlook Calendar connected successfully!"

---

## 🍎 Apple Calendar Configuration

**No API keys needed!** Apple Calendar uses iCal file downloads.

### How It Works

1. **iCal File Generation:**
   - System automatically generates `.ics` files for appointments
   - Files are downloadable from appointment confirmation page
   - Compatible with all calendar apps (Apple Calendar, Google Calendar, Outlook, Thunderbird, etc.)

2. **Usage:**
   - After booking, click "Add to Calendar (iCal)" button
   - File downloads automatically
   - Double-click to add to your default calendar app
   - Or import manually into any calendar application

3. **CalDAV Support (Advanced):**
   - For server-based sync, CalDAV credentials can be configured in staff profile
   - Requires CalDAV server setup (iCloud, own server, etc.)
   - Currently, iCal download is the primary method

### Testing

1. Book an appointment
2. On confirmation page, click "Add to Calendar (iCal)"
3. File should download: `appointment-{id}.ics`
4. Open with your calendar app
5. Event should appear in your calendar

---

## 🔧 Complete `.env` Configuration

```env
# Google Calendar
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/calendar-sync/google/callback/

# Microsoft Outlook Calendar
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret
MICROSOFT_TENANT_ID=common
MICROSOFT_REDIRECT_URI=http://localhost:8000/calendar-sync/outlook/callback/

# Apple Calendar - No configuration needed (uses iCal downloads)
```

---

## 🚀 Quick Setup Checklist

### Google Calendar
- [ ] Create Google Cloud project
- [ ] Enable Google Calendar API
- [ ] Configure OAuth consent screen
- [ ] Create OAuth 2.0 credentials
- [ ] Add redirect URI
- [ ] Copy Client ID and Secret
- [ ] Add to `.env` file
- [ ] Test connection from staff dashboard

### Microsoft Outlook
- [ ] Register app in Azure Portal
- [ ] Configure redirect URI
- [ ] Add API permissions (Calendars.ReadWrite, offline_access)
- [ ] Create client secret
- [ ] Copy Application ID, Client Secret, Tenant ID
- [ ] Add to `.env` file
- [ ] Test connection from staff dashboard

### Apple Calendar
- [ ] No setup needed!
- [ ] Test iCal download from appointment confirmation

---

## 📝 Production Configuration

### Update Redirect URIs

**Before deploying to production:**

1. **Google Calendar:**
   - Add production redirect URI in Google Cloud Console
   - Update `GOOGLE_REDIRECT_URI` in `.env`:
     ```env
     GOOGLE_REDIRECT_URI=https://yourdomain.com/calendar-sync/google/callback/
     ```

2. **Microsoft Outlook:**
   - Add production redirect URI in Azure Portal
   - Update `MICROSOFT_REDIRECT_URI` in `.env`:
     ```env
     MICROSOFT_REDIRECT_URI=https://yourdomain.com/calendar-sync/outlook/callback/
     ```

### Security Considerations

1. **Token Storage:**
   - OAuth tokens are stored in `staff.calendar_data` JSON field
   - Consider encrypting sensitive data in production
   - Use environment variables for all credentials

2. **HTTPS Required:**
   - OAuth redirects require HTTPS in production
   - Ensure your production server uses HTTPS
   - Update redirect URIs to use `https://`

3. **Token Refresh:**
   - Tokens automatically refresh when expired
   - Refresh tokens are stored securely
   - Monitor token expiry in logs

---

## 🆘 Troubleshooting

### Google Calendar Issues

**"Redirect URI mismatch" error:**
- Check redirect URI in Google Cloud Console matches exactly
- Ensure no trailing slashes or protocol mismatches
- For development: Use `http://localhost:8000`
- For production: Use `https://yourdomain.com`

**"Access blocked" error:**
- OAuth consent screen may need verification
- Add test users in OAuth consent screen
- For production, app may need verification by Google

**Token refresh fails:**
- Check if refresh token is stored in `staff.calendar_data`
- Verify `GOOGLE_CLIENT_SECRET` is correct
- Check token expiry in database

### Microsoft Outlook Issues

**"AADSTS50011: Redirect URI mismatch" error:**
- Check redirect URI in Azure Portal matches exactly
- Ensure protocol (http/https) matches
- Check for trailing slashes

**"Insufficient privileges" error:**
- Verify API permissions are added
- Grant admin consent if needed
- Check if user has permission to access calendars

**Token refresh fails:**
- Verify `MICROSOFT_CLIENT_SECRET` is correct
- Check `MICROSOFT_TENANT_ID` (use `common` for personal accounts)
- Verify refresh token is stored

### Apple Calendar Issues

**iCal file doesn't open:**
- Verify file extension is `.ics`
- Check file content (should start with `BEGIN:VCALENDAR`)
- Try importing manually into calendar app

**iCal file missing information:**
- Check appointment has all required fields
- Verify customer appointment exists
- Check logs for generation errors

---

## ✅ Verification Checklist

After configuration, verify everything works:

- [ ] **Google Calendar:**
  - [ ] Can connect from staff dashboard
  - [ ] OAuth flow completes successfully
  - [ ] Calendar shows as connected
  - [ ] Appointment creates calendar event
  - [ ] Calendar event appears in Google Calendar

- [ ] **Microsoft Outlook:**
  - [ ] Can connect from staff dashboard
  - [ ] OAuth flow completes successfully
  - [ ] Calendar shows as connected
  - [ ] Appointment creates calendar event
  - [ ] Calendar event appears in Outlook

- [ ] **Apple Calendar:**
  - [ ] iCal file downloads from confirmation page
  - [ ] File opens in calendar app
  - [ ] Event appears with correct details
  - [ ] Date/time are correct

- [ ] **Automatic Sync:**
  - [ ] New appointment syncs to calendar
  - [ ] Updated appointment updates calendar event
  - [ ] Deleted appointment removes calendar event

---

**Last Updated:** December 2025
**Status:** Complete Configuration Guide

