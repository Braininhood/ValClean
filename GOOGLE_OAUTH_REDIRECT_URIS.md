# Google Cloud OAuth - Required Redirect URIs & JavaScript Origins

## ✅ Your OAuth Credentials

- **Client ID**: `YOUR_GOOGLE_CLIENT_ID`
- **Client Secret**: `YOUR_GOOGLE_CLIENT_SECRET`

---

## 🔧 Configure in Google Cloud Console

Go to: **https://console.cloud.google.com/apis/credentials**

Click on your OAuth 2.0 Client ID, then configure:

---

## 📍 Authorized JavaScript Origins

Add these URLs (one per line):

### Local Development:
```
http://localhost:3000
http://localhost:8000
```

### Production (replace `yourdomain.com` with your actual domain):
```
https://yourdomain.com
https://api.yourdomain.com
```

---

## 🔄 Authorized Redirect URIs

Add **BOTH** of these URLs (one per line):

### Local Development:
```
http://localhost:8000/api/aut/google/callback/
http://localhost:8000/api/calendar/google/callback/
```

### Production (replace `yourdomain.com` with your actual domain):
```
https://yourdomain.com/api/aut/google/callback/
https://yourdomain.com/api/calendar/google/callback/
```

**OR if your API is on a subdomain:**
```
https://api.yourdomain.com/api/aut/google/callback/
https://api.yourdomain.com/api/calendar/google/callback/
```

---

## 📋 Quick Copy-Paste List

### For Local Development - Copy These:

**JavaScript Origins:**
- `http://localhost:3000`
- `http://localhost:8000`

**Redirect URIs:**
- `http://localhost:8000/api/aut/google/callback/`
- `http://localhost:8000/api/calendar/google/callback/`

### For Production - Copy These (replace `yourdomain.com`):

**JavaScript Origins:**
- `https://yourdomain.com`
- `https://api.yourdomain.com` (if API is on subdomain)

**Redirect URIs:**
- `https://yourdomain.com/api/aut/google/callback/`
- `https://yourdomain.com/api/calendar/google/callback/`

---

## ✅ What Each Redirect URI Is For

1. **`/api/aut/google/callback/`** - Used for **Google login/authentication**
   - When users click "Sign in with Google"
   - Google redirects here after user authorizes
   - Backend creates/logs in user and returns JWT tokens

2. **`/api/calendar/google/callback/`** - Used for **Google Calendar sync**
   - When users connect their Google Calendar
   - Google redirects here after user authorizes calendar access
   - Backend stores calendar tokens for syncing appointments

---

## 🚨 Important Notes

- **Both redirect URIs are required** - one for login, one for calendar
- **Trailing slashes matter** - make sure URLs end with `/`
- **HTTP vs HTTPS** - use `http://` for local dev, `https://` for production
- **Exact match required** - URLs must match exactly (including port numbers)

---

## ✅ After Adding These

1. Click **"Save"** in Google Cloud Console
2. Restart your Django server
3. Test the login flow
4. Test calendar sync (separately)

---

**Need Help?** See `GOOGLE_OAUTH_LOGIN_SETUP.md` for complete setup instructions.
