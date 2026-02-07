# Email Environment Setup - Complete ✅

## 📧 Your Gmail Email Configuration

**Email:** `dommovoy@gmail.com`  
**App Password:** `ruym votz yhuw qfsu`

---

## ✅ What to Add to `backend/.env`

Open `backend/.env` and add or update these lines:

```bash
# Email Configuration - Google Gmail
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=dommovoy@gmail.com
EMAIL_HOST_PASSWORD=ruym votz yhuw qfsu
DEFAULT_FROM_EMAIL=dommovoy@gmail.com
```

**Important Notes:**
- `EMAIL_HOST_PASSWORD` can have spaces: `ruym votz yhuw qfsu`
- Or remove spaces: `ruymvotzyhuwqfsu` (both work)
- `EMAIL_HOST_USER` is your full Gmail address
- `DEFAULT_FROM_EMAIL` is where emails will appear to come from

---

## 📝 Full Example `.env` Section

```bash
# ============================================
# Email Configuration - Google Gmail
# ============================================
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=dommovoy@gmail.com
EMAIL_HOST_PASSWORD=ruym votz yhuw qfsu
DEFAULT_FROM_EMAIL=dommovoy@gmail.com
```

---

## ✅ Verification Steps

### 1. Check `.env` File Location

Make sure you're editing: `d:\VALClean\backend\.env` (not `env.example`)

### 2. Restart Django Server

After updating `.env`, restart the server:

```powershell
cd d:\VALClean\backend
# Stop current server (Ctrl+C if running)
.\venv\Scripts\python.exe manage.py runserver
```

### 3. Test Email (Django Shell)

```powershell
cd d:\VALClean\backend
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
    recipient_list=['dommovoy@gmail.com'],  # Send to yourself to test
    fail_silently=False,
)
```

**Expected:** Email should arrive in your Gmail inbox.

### 4. Test with Real Order

1. Create a test order in the system
2. Confirm the order (change status to 'confirmed')
3. Check email inbox - should receive booking confirmation email

---

## 🔧 Settings Already Configured

The Django settings are already configured to read from `.env`:

**File:** `backend/config/settings/base.py` (lines 252-258)

```python
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@valclean.uk')
```

**No code changes needed** - just add to `.env`!

---

## ✅ Summary

**What to do:**
1. Open `backend/.env` file
2. Add email configuration (copy from above)
3. Restart Django server
4. Test email sending

**That's it!** Emails will work when orders are confirmed.

---

## 📧 What Happens When Order Confirmed

When an order status changes to 'confirmed':

1. ✅ **Appointments created** (from order items)
2. ✅ **Calendar sync** (if users have sync enabled)
3. ✅ **Confirmation email sent** → `dommovoy@gmail.com` sends to customer

**Email includes:**
- Order number
- Service details
- Scheduled date/time
- Service address
- Tracking link

---

## 🔐 Security Note

- ✅ `.env` file is in `.gitignore` (not committed to git)
- ✅ App Password is secure (not your regular Gmail password)
- ✅ Keep `.env` file secure
