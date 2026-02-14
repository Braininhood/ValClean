# Google Gmail Email Setup Guide

## 📧 Using Google Gmail for Email Notifications

This guide shows how to set up Google Gmail (Gmail SMTP) to send emails from your VALClean application.

---

## 🔑 What You Need from Google

### Option 1: Gmail Account (Personal/Business)

**Requirements:**
1. **Gmail account** (e.g., `yourname@gmail.com`)
2. **App Password** (not your regular password!)
   - Two-factor authentication (2FA) must be enabled
   - Generate app password from Google Account settings

### Option 2: Google Workspace (Business Gmail)

**Requirements:**
1. **Google Workspace account** (e.g., `support@yourbusiness.com`)
2. **App Password** (if 2FA enabled) OR regular password (if 2FA disabled)
3. **Admin access** to enable "Less secure app access" (if using regular password)

---

## 📋 Step-by-Step Setup

### Step 1: Enable 2-Factor Authentication (Required for App Passwords)

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Click **"2-Step Verification"**
3. Follow the setup process to enable 2FA
4. Complete verification

**Why?** Google requires 2FA to generate App Passwords (more secure than regular passwords).

---

### Step 2: Generate App Password

**IMPORTANT:** "App passwords" may not be visible on the 2-Step Verification page. Use one of these methods:

#### Method 1: Direct Link (Easiest)

1. Go directly to: **[App Passwords](https://myaccount.google.com/apppasswords)**
2. You may need to sign in again
3. If you see "App passwords" page → Skip to step 4 below
4. If you see "2-Step Verification" page → Use Method 2 below

#### Method 2: Via 2-Step Verification Page

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Click **"2-Step Verification"**
3. **Scroll to the very bottom** of the page
4. Look for **"App passwords"**
   - It may be below all the verification methods
   - It might be in a separate section at the bottom
5. If still not visible, use **Method 3** below

#### Method 3: Alternative Path

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Look for **"How you sign in to Google"** section (not "2-Step Verification")
3. Click **"App passwords"** if visible
4. If not found, use **Method 1** (direct link) above

#### Method 4: If "App passwords" Option Doesn't Appear

**Possible reasons:**
- Account doesn't have 2FA fully enabled
- Personal Google Account may need "Less secure app access" instead (not recommended)
- Google Workspace accounts may have different settings

**Alternative:** Use OAuth2 with Google API (more secure, but requires Google Cloud Console setup)

---

### Once You Find "App Passwords" Page:

1. Select app: **"Mail"**
2. Select device: **"Other (Custom name)"**
3. Enter name: **"VALClean Email Service"**
4. Click **"Generate"**
5. **Copy the 16-character password** (you'll see it only once!)
   - Format: `abcd efgh ijkl mnop` (may have spaces)
   - Remove spaces if needed: `abcdefghijklmnop`

**Example App Password:** `abcd efgh ijkl mnop`

**Important:** 
- This is a 16-character password (with or without spaces)
- Use this password in `.env`, NOT your regular Gmail password
- Keep it secure!

---

### Step 3: Add to .env File

Open `backend/.env` and add:

```bash
# Email Configuration - Google Gmail
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

**Example:**
```bash
# Email Configuration - Google Gmail
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=support@valclean.uk
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
DEFAULT_FROM_EMAIL=support@valclean.uk
```

**Notes:**
- `EMAIL_HOST_USER`: Your Gmail address (full email)
- `EMAIL_HOST_PASSWORD`: The 16-character App Password (with or without spaces)
- `DEFAULT_FROM_EMAIL`: The "From" address in emails (usually same as `EMAIL_HOST_USER`)

---

## ⚙️ Configuration Options

### Standard Gmail SMTP (Port 587 - TLS)

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Alternative: Port 465 (SSL)

If port 587 doesn't work, try port 465 with SSL:

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## 🧪 Testing Email Configuration

### Test 1: Django Shell

```powershell
cd backend
.\venv\Scripts\python.exe manage.py shell
```

Then:
```python
from django.core.mail import send_mail
from django.conf import settings

# Test email
send_mail(
    subject='Test Email from VALClean',
    message='This is a test email to verify Gmail configuration.',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=['your-test-email@gmail.com'],
    fail_silently=False,
)
```

**Expected:** Email should arrive in your test inbox.

### Test 2: Confirm an Order

1. Create a test order
2. Confirm the order in admin
3. Check customer's email inbox for confirmation email

---

## 🔐 Security Best Practices

### ✅ DO:
- ✅ Use **App Passwords** (not regular Gmail passwords)
- ✅ Store credentials in `.env` (not in code)
- ✅ Keep `.env` in `.gitignore` (never commit to git)
- ✅ Use a dedicated Gmail account for sending emails
- ✅ Enable 2FA on the Gmail account

### ❌ DON'T:
- ❌ Use your regular Gmail password
- ❌ Commit email credentials to git
- ❌ Share App Passwords publicly
- ❌ Use your personal Gmail for production

---

## 📊 Email Limits (Gmail)

**Gmail Free Account:**
- **Daily sending limit:** 500 emails/day
- **Rate limit:** ~100 emails/hour

**Google Workspace (Business):**
- **Daily sending limit:** 2,000 emails/day (standard)
- **Rate limit:** ~100 emails/hour

**Recommendation:** For production with high volume, consider:
- Google Workspace (higher limits)
- SendGrid (better for transactional emails)
- Resend (modern email API)

---

## 🔄 Switching to Other Email Providers

The email service is designed to support multiple providers. Just change settings in `.env`:

### SendGrid

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=your-email@yourdomain.com
```

### Resend

```bash
# Requires django-resend package
EMAIL_BACKEND=resend.django.backend.ResendBackend
RESEND_API_KEY=your-resend-api-key
DEFAULT_FROM_EMAIL=your-email@yourdomain.com
```

### Generic SMTP

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yourdomain.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@yourdomain.com
EMAIL_HOST_PASSWORD=your-password
DEFAULT_FROM_EMAIL=your-email@yourdomain.com
```

---

## ✅ Verification Checklist

- [ ] Gmail account created/configured
- [ ] 2FA enabled on Gmail account
- [ ] App Password generated
- [ ] Credentials added to `backend/.env`
- [ ] Test email sent successfully
- [ ] Booking confirmation email works

---

## 🐛 Troubleshooting

### "Invalid credentials" Error

**Problem:** Gmail rejects login attempt

**Solutions:**
1. Check App Password is correct (16 characters)
2. Ensure 2FA is enabled
3. Try removing spaces from App Password
4. Verify `EMAIL_HOST_USER` is correct email address

### "Connection refused" Error

**Problem:** Can't connect to Gmail SMTP

**Solutions:**
1. Check firewall allows port 587/465
2. Try port 465 with SSL instead of 587 with TLS
3. Verify `EMAIL_HOST` is `smtp.gmail.com`

### Emails Not Sending

**Problem:** No errors but emails don't arrive

**Solutions:**
1. Check spam/junk folder
2. Verify recipient email is correct
3. Check Gmail daily sending limit (500/day)
4. Check Django logs for errors

---

## 📝 Summary

**To use Google Gmail:**
1. Enable 2FA on Gmail account
2. Generate App Password
3. Add credentials to `backend/.env`
4. Done! ✅

**Email service is flexible** - can switch to SendGrid, Resend, or any SMTP provider by changing `.env` settings.
