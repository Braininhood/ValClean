# Calendar Sync - Simple Explanation

## 🎯 Quick Answer

**Q: "In .env I can add maximum 1 account. How do different users connect their calendars?"**

**A: The credentials in .env are NOT user accounts - they're YOUR APP'S credentials (like your app's ID card). Each user connects their OWN calendar via OAuth.**

---

## 🔑 How It Works (Simple Version)

### Step 1: Your App Credentials (One-Time Setup in .env)

```bash
# These are YOUR APP'S credentials (like an ID card for your app)
# You get these from Google/Microsoft when you register your app
# NOT user accounts!

GOOGLE_CLIENT_ID=123456-abc.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-secret-here
OUTLOOK_CLIENT_ID=12345678-1234-1234-1234-abc
OUTLOOK_CLIENT_SECRET=secret-here
```

**Important:** These are **application credentials** - everyone uses the same ones!

---

### Step 2: Users Connect Their Personal Calendars (OAuth)

**Customer John wants Google Calendar:**

1. John clicks "Connect Google Calendar" button
2. John is redirected to Google login
3. John logs in with **HIS OWN** Google account (john@gmail.com)
4. John grants permission
5. **John's tokens** stored in John's Profile → `john.profile.calendar_access_token`
6. Done! John's calendar is connected!

**Customer Sarah wants Outlook:**

1. Sarah clicks "Connect Outlook" button
2. Sarah is redirected to Microsoft login
3. Sarah logs in with **HER OWN** Outlook account (sarah@outlook.com)
4. Sarah grants permission
5. **Sarah's tokens** stored in Sarah's Profile → `sarah.profile.calendar_access_token`
6. Done! Sarah's calendar is connected!

---

## 📊 Visual Flow

```
┌─────────────────────────────────────────────────────────┐
│ YOUR APP (.env)                                         │
│                                                         │
│ GOOGLE_CLIENT_ID=123456-abc...     ← App credentials   │
│ GOOGLE_CLIENT_SECRET=secret...     ← App credentials   │
│                                                         │
│ (These are SHARED by all users)                        │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ USER 1: John (Customer)                                 │
│                                                         │
│ John's Profile:                                         │
│   calendar_provider = 'google'                          │
│   calendar_access_token = 'token_for_john@gmail.com'    │
│                                                         │
│ John connects HIS OWN Google Calendar                   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ USER 2: Sarah (Staff)                                   │
│                                                         │
│ Sarah's Profile:                                        │
│   calendar_provider = 'outlook'                         │
│   calendar_access_token = 'token_for_sarah@outlook.com' │
│                                                         │
│ Sarah connects HER OWN Outlook Calendar                 │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ USER 3: Bob (Manager)                                   │
│                                                         │
│ Bob's Profile:                                          │
│   calendar_provider = 'apple'                           │
│   calendar_access_token = NULL (uses .ics files)        │
│                                                         │
│ Bob downloads .ics files to HIS OWN Apple Calendar      │
└─────────────────────────────────────────────────────────┘
```

---

## Google sign-in vs Calendar sync (dev note)

Signing in with Google (or having a Google account) is **separate** from syncing your calendar. Calendar sync uses the **Google Calendar API** and must be enabled and configured by your organisation on the server (e.g. `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` for the Calendar API). If that is not set up, "Connect Google Calendar" will show as temporarily unavailable. Users can still add appointments using **Apple Calendar** and the .ics download link on individual appointment or job pages.

---

## ✅ Summary

### What's in .env:
- ✅ **ONE set of app credentials** (from Google/Microsoft)
- ✅ **Shared by ALL users**
- ✅ **NOT user accounts**

### What's in Database (Profile model):
- ✅ **Each user has their OWN tokens** (`calendar_access_token`)
- ✅ **Different users can use different providers**
- ✅ **Tokens stored separately per user**

### Result:
- ✅ John connects his Google Calendar
- ✅ Sarah connects her Outlook Calendar  
- ✅ Bob uses Apple Calendar (.ics files)
- ✅ All using the SAME app credentials from .env!

---

## 🚀 How Users Actually Connect (Step-by-Step)

### Example: Customer Connecting Calendar

**Frontend (Settings Page):**
```javascript
// User clicks "Connect Google Calendar" button
const response = await fetch('/api/calendar/google/connect/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${userToken}`,
  }
});

const data = await response.json();
// data.authorization_url = "https://accounts.google.com/o/oauth2/auth?..."
window.location.href = data.authorization_url; // Redirect to Google
```

**What Happens:**
1. User redirected to Google login
2. User logs in with their Google account
3. Google shows: "Allow VALClean to access your calendar?"
4. User clicks "Allow"
5. Google redirects back to your app
6. Your app saves tokens to that user's Profile
7. Done! ✅

---

## 💡 Key Point

**The OAuth credentials in .env are like a driver's license for your app - they identify your app to Google/Microsoft, but each user connects their own calendar account!**

No need to:
- ❌ Add individual user accounts to .env
- ❌ Create separate credentials for each user
- ❌ Share calendar passwords

Just:
- ✅ Add app credentials to .env (one time)
- ✅ Let users connect via OAuth (automatic)
- ✅ Tokens stored per user in database

---

## 📝 Example .env File

```bash
# Your App's OAuth Credentials (shared by all users)
GOOGLE_CLIENT_ID=123456789-abcdef.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwxyz
GOOGLE_REDIRECT_URI=http://localhost:8000/api/calendar/google/callback/

OUTLOOK_CLIENT_ID=12345678-1234-1234-1234-123456789abc
OUTLOOK_CLIENT_SECRET=your-secret-from-azure
OUTLOOK_REDIRECT_URI=http://localhost:8000/api/calendar/outlook/callback/
```

**That's it!** Just these app credentials - users connect their own accounts via OAuth.
