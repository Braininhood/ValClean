# Google Cloud OAuth Login Setup - Complete Guide

## ✅ Configuration Complete!

Your Google Cloud OAuth credentials have been configured for **login/authentication**:

- **Client ID**: `YOUR_GOOGLE_CLIENT_ID`
- **Client Secret**: `YOUR_GOOGLE_CLIENT_SECRET`

---

## 🔧 Required Configuration in Google Cloud Console

### Step 1: Add Authorized JavaScript Origins

Go to: https://console.cloud.google.com/apis/credentials

Click on your OAuth 2.0 Client ID, then under **"Authorized JavaScript origins"**, add:

**For Local Development:**
```
http://localhost:3000
http://localhost:8000
```

**For Production:**
```
https://yourdomain.com
https://api.yourdomain.com  (if API is on subdomain)
```

### Step 2: Add Authorized Redirect URIs

Under **"Authorized redirect URIs"**, add **BOTH** of these:

**For Login/Authentication:**
```
http://localhost:8000/api/aut/google/callback/
```

**For Calendar Sync:**
```
http://localhost:8000/api/calendar/google/callback/
```

**For Production, add:**
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

## 📋 Summary of Redirect URIs Needed

### Local Development:
1. `http://localhost:8000/api/aut/google/callback/` - **Login/Authentication**
2. `http://localhost:8000/api/calendar/google/callback/` - **Calendar Sync**

### Production:
1. `https://yourdomain.com/api/aut/google/callback/` - **Login/Authentication**
2. `https://yourdomain.com/api/calendar/google/callback/` - **Calendar Sync**

---

## 🔄 What Changed

### Before (Supabase OAuth):
- Frontend used Supabase client for Google login
- Backend verified Supabase JWT tokens
- Required Supabase configuration

### Now (Google Cloud OAuth):
- Frontend uses Google Cloud OAuth directly
- Backend uses Google Cloud credentials
- No Supabase dependency for authentication
- Same credentials work for both login AND calendar sync

---

## 🚀 Next Steps

1. **Add the redirect URIs** in Google Cloud Console (see above)
2. **Install Python libraries** (if not already installed):
   ```bash
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```
3. **Restart Django server**
4. **Update frontend** to use new Google OAuth endpoints (see frontend changes below)

---

## 📝 Frontend Changes Needed

The frontend needs to be updated to use the new Google Cloud OAuth endpoints instead of Supabase. The new flow:

1. User clicks "Sign in with Google"
2. Frontend calls `GET /api/aut/google/start/`
3. Backend returns `authorization_url`
4. Frontend redirects user to Google OAuth
5. Google redirects to `/api/aut/google/callback/`
6. Backend exchanges code for user info and creates/logs in user
7. Backend redirects to frontend with tokens
8. Frontend stores tokens and redirects to dashboard

---

## ✅ Verification Checklist

- [x] Google Cloud Project created
- [x] Google Calendar API enabled
- [x] OAuth 2.0 Client ID created
- [x] Credentials added to `backend/.env`
- [ ] **Authorized JavaScript origins added** ⚠️ **DO THIS NOW!**
- [ ] **Authorized redirect URIs added** ⚠️ **DO THIS NOW!**
- [ ] Python libraries installed
- [ ] Django server restarted
- [ ] Frontend updated to use new endpoints
- [ ] Test login flow

---

## 🐛 Troubleshooting

### Error: "redirect_uri_mismatch"
**Solution**: Make sure you added BOTH redirect URIs in Google Cloud Console:
- `/api/aut/google/callback/` for login
- `/api/calendar/google/callback/` for calendar

### Error: "origin_mismatch"
**Solution**: Add your frontend URL to "Authorized JavaScript origins":
- `http://localhost:3000` for local dev
- `https://yourdomain.com` for production

### Error: "Library not installed"
**Solution**: Run `pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib`

---

## 📚 Related Documentation

- `GOOGLE_CALENDAR_SETUP_GUIDE.md` - Calendar sync setup
- `GOOGLE_CALENDAR_QUICK_START.md` - Quick reference

---

**Important**: Make sure to add BOTH redirect URIs (login AND calendar) in Google Cloud Console!
