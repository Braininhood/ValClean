# Google OAuth Client Deleted - How to Fix

## ❌ Error: "The OAuth client was deleted" (Error 401: deleted_client)

This error means the Google OAuth client ID configured in your `.env` file was deleted from Google Cloud Console.

---

## 🔧 Solution: Create a New OAuth Client

### Step 1: Go to Google Cloud Console

1. Visit: **https://console.cloud.google.com/apis/credentials**
2. Select your project (or create a new one if needed)

### Step 2: Create OAuth 2.0 Client ID

1. Click **"Create Credentials"** → **"OAuth client ID"**
2. If prompted, configure the OAuth consent screen first:
   - Click **"Configure Consent Screen"**
   - Select **"External"** (unless you have Google Workspace)
   - Fill in:
     - **App name**: `VALClean`
     - **User support email**: Your email
     - **Developer contact**: Your email
   - Click **"Save and Continue"**
   - **Scopes**: Add `openid`, `email`, `profile` (for login)
   - Click **"Save and Continue"** through remaining steps

### Step 3: Create OAuth Client for Login

1. Click **"Create Credentials"** → **"OAuth client ID"**
2. **Application type**: `Web application`
3. **Name**: `VALClean Login`
4. **Authorized JavaScript origins**:
   ```
   http://localhost:3000
   http://localhost:8000
   https://ec2-13-135-109-229.eu-west-2.compute.amazonaws.com
   ```
5. **Authorized redirect URIs**:
   ```
   http://localhost:8000/api/aut/google/callback/
   https://ec2-13-135-109-229.eu-west-2.compute.amazonaws.com/api/aut/google/callback/
   ```
6. Click **"Create"**

### Step 4: Copy New Credentials

You'll see a popup with:
- **Client ID**: `xxxxx-xxxxx.apps.googleusercontent.com`
- **Client Secret**: `GOCSPX-xxxxx`

**Copy these immediately** - you won't see the secret again!

### Step 5: Update backend/.env

Replace the old credentials in `backend/.env`:

```bash
# Google OAuth 2.0 (Google Cloud)
# Login/Authentication credentials (NEW - replace with your new client ID and secret)
GOOGLE_CLIENT_ID=your-new-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-new-client-secret
```

### Step 6: Restart Django Server

```bash
# Stop the server (Ctrl+C)
python manage.py runserver
```

---

## ✅ Verify Setup

1. **Test Google Sign-In**:
   - Go to `/login`
   - Click "Sign in with Google"
   - You should be redirected to Google (not see the deleted client error)

2. **Check Backend Logs**:
   - Make sure no errors about missing credentials

---

## 📝 Important Notes

- **Keep your Client Secret secure** - never commit it to git
- **Use different clients** for login and calendar (as you already have)
- **Calendar client** (`203639182148-1qrm7moj8u7m2gqsf692ms9e34ul7dn3...`) is still valid - don't change it

---

## 🔄 If You Need to Recreate Calendar Client Too

If the calendar client was also deleted, follow the same steps but:
- **Name**: `VALClean Calendar`
- **Redirect URI**: `http://localhost:8000/api/calendar/google/callback/`
- Update `GOOGLE_CALENDAR_CLIENT_ID` and `GOOGLE_CALENDAR_CLIENT_SECRET` in `.env`

---

**After updating credentials, restart Django server and test again!**
