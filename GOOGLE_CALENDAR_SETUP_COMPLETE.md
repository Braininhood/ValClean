# Google Calendar OAuth Setup - Configuration Complete ✅

## ✅ What Has Been Configured

Your Google Calendar OAuth credentials have been added to `backend/.env`:

```bash
GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI=http://localhost:8000/api/calendar/google/callback/
```

## 🔐 Important: Two Different OAuth Systems

### 1. **Supabase OAuth** (Authentication)
- **Purpose**: User login/authentication (Google sign-in)
- **Where**: Supabase Dashboard → Authentication → Providers → Google
- **Used for**: Users logging in with their Google account
- **Status**: ✅ Already configured and working

### 2. **Google Cloud OAuth** (Calendar Sync)
- **Purpose**: Calendar synchronization (sync appointments to Google Calendar)
- **Where**: Google Cloud Console → APIs & Services → Credentials
- **Used for**: Syncing appointments to users' Google Calendars
- **Status**: ✅ Just configured

**These are SEPARATE and both are needed!**

---

## ⚠️ IMPORTANT: Configure Redirect URI in Google Cloud Console

Before testing, you **MUST** add the redirect URI in Google Cloud Console:

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click on your OAuth 2.0 Client ID (the one ending in `.apps.googleusercontent.com`)
3. Under **"Authorized redirect URIs"**, click **"Add URI"**
4. Add: `http://localhost:8000/api/calendar/google/callback/`
5. Click **"Save"**

**For Production:**
- Add: `https://yourdomain.com/api/calendar/google/callback/`
- Replace `yourdomain.com` with your actual production domain

---

## 📋 Next Steps

### 1. Install Required Python Libraries

```bash
cd backend
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

Or if using a virtual environment:
```bash
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 2. Restart Django Server

After adding the credentials, restart your Django server:

```bash
# Stop the server (Ctrl+C)
# Then restart
python manage.py runserver
```

### 3. Test the Integration

1. **Start your servers:**
   - Backend: `python manage.py runserver` (port 8000)
   - Frontend: `npm run dev` (port 3000)

2. **Log in** to your application (using Supabase OAuth or regular login)

3. **Navigate to Calendar Settings:**
   - Go to: `/settings/calendar` (or wherever your calendar settings page is)

4. **Connect Google Calendar:**
   - Click "Connect Google Calendar" button
   - You'll be redirected to Google's OAuth consent screen
   - Sign in with your Google account
   - Grant permissions to access your calendar
   - You'll be redirected back to your app

5. **Verify Connection:**
   - Check that the status shows "Connected"
   - Create a test appointment
   - Check your Google Calendar - the appointment should appear!

---

## 🔍 Verification Checklist

- [x] Google Cloud Project created
- [x] Google Calendar API enabled
- [x] OAuth 2.0 Client ID created
- [x] Credentials added to `backend/.env`
- [ ] **Redirect URI added in Google Cloud Console** ⚠️ **DO THIS NOW!**
- [ ] Python libraries installed
- [ ] Django server restarted
- [ ] Test connection successful
- [ ] Appointments syncing to Google Calendar

---

## 🐛 Troubleshooting

### Error: "redirect_uri_mismatch"
**Solution**: Make sure you added `http://localhost:8000/api/calendar/google/callback/` to the **Authorized redirect URIs** in Google Cloud Console.

### Error: "Google OAuth credentials not configured"
**Solution**: 
- Check that `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are in `backend/.env`
- Restart Django server after adding them

### Error: "Library not installed"
**Solution**: Run `pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib`

### Appointments not syncing
**Solution**:
- Verify the user has connected their calendar
- Check appointment status is `confirmed` or `in_progress`
- Check Django logs for errors

---

## 📝 Production Deployment

When deploying to production:

1. ✅ Update `GOOGLE_REDIRECT_URI` in production `.env`:
   ```bash
   GOOGLE_REDIRECT_URI=https://yourdomain.com/api/calendar/google/callback/
   ```

2. ✅ Add production redirect URI in Google Cloud Console:
   - Go to OAuth 2.0 Client ID settings
   - Add: `https://yourdomain.com/api/calendar/google/callback/`

3. ✅ Add production JavaScript origin:
   - Add: `https://yourdomain.com`

4. ✅ Test OAuth flow on production domain

---

## ✅ Summary

- **Supabase OAuth**: Used for user authentication (login with Google) ✅ Already working
- **Google Cloud OAuth**: Used for calendar sync (sync appointments) ✅ Just configured
- **Next Step**: Add redirect URI in Google Cloud Console, then test!

---

**Need Help?** Check `GOOGLE_CALENDAR_SETUP_GUIDE.md` for detailed instructions.
