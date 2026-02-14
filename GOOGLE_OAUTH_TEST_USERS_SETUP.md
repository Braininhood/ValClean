# Google OAuth Test Users Setup

## Problem
You're seeing this error:
```
Access blocked: ValClean has not completed the Google verification process
Error 403: access_denied
```

This happens because your Google OAuth app is in **Testing** mode and only approved test users can sign in.

## Solution: Add Test Users

### Step 1: Go to Google Cloud Console
1. Open [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (the one with your OAuth client)

### Step 2: Navigate to OAuth Consent Screen
1. Go to **APIs & Services** → **OAuth consent screen**
2. Or direct link: `https://console.cloud.google.com/apis/credentials/consent`

### Step 3: Add Test Users
1. Scroll down to the **"Test users"** section
2. Click **"+ ADD USERS"**
3. Enter the email addresses that should be able to sign in:
   - `DOMMOVOY@gmail.com` (your email)
   - Any other emails that need access
4. Click **"ADD"**

### Step 4: Save Changes
- Click **"SAVE AND CONTINUE"** at the bottom

## Important Notes

### Testing Mode Limitations
- **Only test users** can sign in
- Maximum **100 test users** allowed
- Users outside the list will see the "access_denied" error

### For Production (Later)
When you're ready to make the app public:
1. Complete Google's **OAuth verification process**
2. Submit your app for review
3. Once approved, change from "Testing" to "Production"
4. Then **anyone** can sign in (no test user list needed)

### Quick Fix for Now
**Add these emails as test users:**
- `DOMMOVOY@gmail.com`
- Any other emails you need for testing

After adding test users, they should be able to sign in immediately (no need to wait for approval).

## Verification Process (For Production)

If you want to publish the app later, you'll need to:
1. Complete the OAuth consent screen configuration
2. Add privacy policy URL
3. Add terms of service URL
4. Submit for Google verification
5. Wait for approval (can take days/weeks)

For now, **adding test users is the fastest solution**.
