# Calendar Sync User Guide - How Different Roles Connect Their Calendars

## 📖 Understanding OAuth (Important!)

### ❓ Common Question: "Do I need to add user accounts in .env?"

**Answer: NO!** The OAuth credentials in `.env` are **application-level credentials** (like your app's ID), not user accounts.

### How OAuth Works:

1. **Application Credentials** (in `.env` - ONE set for entire app):
   ```bash
   GOOGLE_CLIENT_ID=your-app-id-from-google      # Your app's ID (not a user account!)
   GOOGLE_CLIENT_SECRET=your-app-secret           # Your app's secret (not a user password!)
   OUTLOOK_CLIENT_ID=your-app-id-from-azure       # Your app's ID
   OUTLOOK_CLIENT_SECRET=your-app-secret          # Your app's secret
   ```

2. **User Accounts** (each user connects their own):
   - Customer John connects his personal Google Calendar
   - Staff Member Sarah connects her personal Outlook Calendar
   - Manager Bob connects his personal Apple Calendar (via .ics download)
   - Each user uses their own calendar account

### The OAuth Flow:

```
1. User clicks "Connect Google Calendar" button
2. User is redirected to Google login
3. User logs in with THEIR Google account
4. User grants permission to your app
5. Google sends tokens back to your app
6. Tokens stored in user's Profile (calendar_access_token)
7. User's calendar is now connected!
```

**Result:** Each user connects their OWN calendar account - no need to add user accounts in `.env`!

---

## 👥 How Different Roles Connect Calendars

### Customer Role

**Use Case:** Customer wants appointment reminders in their personal calendar

**Steps:**
1. Customer logs into their account
2. Goes to Settings → Calendar Sync
3. Chooses calendar provider:
   - **Google Calendar**: Click "Connect Google" → OAuth flow → Connected!
   - **Microsoft Outlook**: Click "Connect Outlook" → OAuth flow → Connected!
   - **Apple Calendar**: Click "Download .ics" → Import to Apple Calendar

**What Happens:**
- When customer's order is confirmed → Appointment automatically added to their calendar
- Customer sees appointment in their Google/Outlook/Apple Calendar

---

### Staff Role

**Use Case:** Staff member wants their work schedule in their personal calendar

**Steps:**
1. Staff member logs into staff portal
2. Goes to Settings → Calendar Sync
3. Chooses calendar provider (same options as customer)

**What Happens:**
- When staff is assigned to an appointment → Event automatically added to their calendar
- Staff sees all their appointments in their personal calendar
- Event includes: Customer name, address, phone, service details

---

### Manager Role

**Use Case:** Manager wants to see all staff appointments in their calendar

**Steps:**
1. Manager logs into manager portal
2. Goes to Settings → Calendar Sync
3. Chooses calendar provider

**What Happens:**
- When staff member has an appointment → Event added to manager's calendar
- Manager sees all team appointments in their personal calendar
- Event includes: Staff name, customer info, service details

---

### Admin Role

**Use Case:** Admin wants to sync all appointments to their calendar

**Steps:**
1. Admin logs into admin panel
2. Goes to Settings → Calendar Sync
3. Chooses calendar provider

**What Happens:**
- When any appointment is created → Event added to admin's calendar
- Admin sees all system appointments in their personal calendar

---

## 🔧 Setting Up OAuth Credentials (One-Time Setup)

You only need **ONE set of OAuth credentials** in `.env` for the entire application. These are **application credentials**, not user accounts.

### Google Calendar Setup:

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
2. **Create a project** (or use existing)
3. **Enable Google Calendar API**
4. **Create OAuth 2.0 Credentials**:
   - Go to "Credentials" → "Create Credentials" → "OAuth client ID"
   - Application type: "Web application"
   - Authorized redirect URIs: `http://localhost:8000/api/calendar/google/callback/`
   - Copy **Client ID** and **Client Secret**

5. **Add to `.env`**:
   ```bash
   GOOGLE_CLIENT_ID=123456789-abcdefg.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=GOCSPX-your-secret-here
   GOOGLE_REDIRECT_URI=http://localhost:8000/api/calendar/google/callback/
   ```

### Microsoft Outlook Setup:

1. **Go to [Azure Portal](https://portal.azure.com/)**
2. **Register an application**:
   - Go to "Azure Active Directory" → "App registrations" → "New registration"
   - Name: "VALClean Calendar Sync"
   - Redirect URI: `http://localhost:8000/api/calendar/outlook/callback/` (Web platform)

3. **Add API Permissions**:
   - Go to "API permissions" → "Add a permission"
   - Microsoft Graph → Delegated permissions
   - Select: `Calendars.ReadWrite`
   - Grant admin consent

4. **Create Client Secret**:
   - Go to "Certificates & secrets" → "New client secret"
   - Copy the secret value

5. **Add to `.env`**:
   ```bash
   OUTLOOK_CLIENT_ID=12345678-1234-1234-1234-123456789abc
   OUTLOOK_CLIENT_SECRET=your-secret-value-here
   OUTLOOK_REDIRECT_URI=http://localhost:8000/api/calendar/outlook/callback/
   ```

**Important:** These credentials are shared by ALL users - each user connects their own personal account via OAuth!

---

## 📱 User Experience Flow

### Example: Customer Connecting Google Calendar

1. **Customer visits:** `http://localhost:3000/settings/calendar`
2. **Clicks:** "Connect Google Calendar" button
3. **Frontend calls:** `POST /api/calendar/google/connect/`
4. **Backend returns:** `{ authorization_url: "https://accounts.google.com/..." }`
5. **Frontend redirects user to:** Google OAuth page
6. **User logs in with their Google account**
7. **User grants permission** ("Allow VALClean to access your calendar")
8. **Google redirects back to:** `http://localhost:8000/api/calendar/google/callback/`
9. **Backend saves tokens** to user's Profile
10. **Backend redirects to:** `http://localhost:3000/settings/calendar?connected=google`
11. **Frontend shows:** "Google Calendar Connected!" ✅

**Now when customer's order is confirmed:**
- Appointment automatically appears in customer's Google Calendar
- No manual action needed!

---

## 🎯 Key Points

### ✅ What's Correct:
- **ONE set of OAuth credentials** in `.env` (application credentials)
- **Each user connects their own calendar** (via OAuth flow)
- **Different users can use different providers**:
  - Customer A → Google Calendar
  - Customer B → Outlook Calendar
  - Staff Member → Apple Calendar (via .ics)
- **Tokens stored per user** in `Profile` model

### ❌ What's NOT Needed:
- Adding individual user accounts to `.env`
- Creating separate OAuth credentials for each user
- Sharing calendar credentials between users

---

## 💡 Example Scenarios

### Scenario 1: Customer with Google Calendar
```
Customer: john@example.com
Role: customer
Calendar Provider: Google Calendar
Own Google Account: john@gmail.com

Flow:
1. John logs into VALClean as john@example.com
2. Connects his Google Calendar (john@gmail.com)
3. Order confirmed → Event added to john@gmail.com's calendar
```

### Scenario 2: Staff with Outlook Calendar
```
Staff: sarah@valclean.com
Role: staff
Calendar Provider: Microsoft Outlook
Own Outlook Account: sarah@outlook.com

Flow:
1. Sarah logs into VALClean as sarah@valclean.com
2. Connects her Outlook Calendar (sarah@outlook.com)
3. Assigned to appointment → Event added to sarah@outlook.com's calendar
```

### Scenario 3: Manager with Apple Calendar
```
Manager: bob@valclean.com
Role: manager
Calendar Provider: Apple Calendar
Uses iPhone/Mac Calendar app

Flow:
1. Bob logs into VALClean as bob@valclean.com
2. Downloads .ics file for appointment
3. Imports .ics file into Apple Calendar app
4. Appointment appears in Bob's iPhone/Mac Calendar
```

---

## 🔐 Security Notes

1. **Tokens are encrypted** (stored in `Profile.calendar_access_token`)
2. **Each user's tokens are separate** (not shared)
3. **OAuth credentials in .env are safe** (they're application-level, not user passwords)
4. **Users can disconnect** anytime (removes their tokens)

---

## 📞 Support

If users have questions about connecting calendars:
- **Google Calendar**: They need a Google account (Gmail or Google Workspace)
- **Microsoft Outlook**: They need a Microsoft account (Outlook.com, Hotmail, or Office 365)
- **Apple Calendar**: They can download .ics files and import to any calendar app

**No technical setup required from users** - just click "Connect" and follow the OAuth flow!
