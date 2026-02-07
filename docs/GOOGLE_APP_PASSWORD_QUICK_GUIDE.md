# Google App Password - Quick Guide

## 🎯 Easiest Method (Direct Link)

**Don't look for it in the 2-Step Verification page - use the direct link!**

### Step 1: Go Directly to App Passwords

Open this link in your browser:
**👉 [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)**

You may need to sign in to your Google account.

### Step 2: Generate App Password

Once on the App Passwords page:

1. **Select app:** Choose **"Mail"** (or **"Почта"** in Russian)
2. **Select device:** Choose **"Other (Custom name)"** (or **"Другое"**)
3. **Enter name:** Type **"VALClean Email Service"**
4. **Click "Generate"** (or **"Создать"**)

### Step 3: Copy the Password

You'll see a **16-character password** like:
- `abcd efgh ijkl mnop` (with spaces)
- Or: `abcdefghijklmnop` (without spaces)

**Copy this password immediately** - you can only see it once!

### Step 4: Add to .env

Add to `backend/.env`:

```bash
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
```

(You can remove spaces or keep them - both work)

---

## ⚠️ If Direct Link Doesn't Work

### Check These:

1. **2FA Must Be Enabled**
   - App Passwords only appear if 2-Step Verification is ON
   - Verify at: [https://myaccount.google.com/security](https://myaccount.google.com/security)

2. **Account Type Restrictions**
   - Personal Gmail: ✅ Works
   - Google Workspace (Business): ⚠️ May require admin approval
   - School/Organization accounts: ❌ May be blocked

3. **Advanced Protection Enabled?**
   - If your account has Advanced Protection, App Passwords may be disabled
   - Check: [https://myaccount.google.com/security](https://myaccount.google.com/security)

---

## 🔍 Alternative: Find It in Security Settings

If direct link doesn't work, try:

1. Go to: [https://myaccount.google.com/security](https://myaccount.google.com/security)
2. Look for section: **"Signing in to Google"**
3. Under **"2-Step Verification"**, scroll down
4. Look for **"App passwords"** (may be at the bottom of that section)

**Note:** In some Google Account layouts, "App passwords" might be in a different location or require clicking into "2-Step Verification" first.

---

## 💡 Why App Passwords Are Needed

**App Passwords are required because:**
- Gmail doesn't allow regular passwords for apps (security)
- You need a special 16-character password for SMTP access
- This is separate from your Google login password
- More secure than "Less secure app access"

---

## ✅ Quick Checklist

- [ ] 2-Step Verification is enabled
- [ ] Tried direct link: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
- [ ] Generated App Password (16 characters)
- [ ] Copied password before closing the page
- [ ] Added to `backend/.env` as `EMAIL_HOST_PASSWORD`

---

## 📞 Still Can't Find It?

**Possible reasons:**
1. 2FA not fully enabled (complete setup process)
2. Account type doesn't support App Passwords (Workspace admin restriction)
3. Advanced Protection enabled (blocks App Passwords)
4. UI changed (try direct link: `myaccount.google.com/apppasswords`)

**Try this:**
- Use direct link: **[myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)**
- If it redirects or shows error, your account may not support App Passwords
- Consider using Google Workspace SMTP (different setup) or alternative email service
