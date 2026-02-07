# Gmail Email Setup - Environment Variables

## 📧 Your Email Configuration

**Email:** `dommovoy@gmail.com`  
**App Password:** `ruym votz yhuw qfsu`

---

## ✅ Add to `backend/.env`

Open the file: `d:\VALClean\backend\.env`

Add or update these lines:

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

**Important:**
- File location: `backend\.env` (not `env.example`)
- `.env` file is gitignored (safe for secrets)
- Restart Django server after updating `.env`

---

## 📝 Quick Copy-Paste

Just add this to `backend/.env`:

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=dommovoy@gmail.com
EMAIL_HOST_PASSWORD=ruym votz yhuw qfsu
DEFAULT_FROM_EMAIL=dommovoy@gmail.com
```

---

## ✅ Test Email

After adding to `.env` and restarting server:

**Django Shell:**
```powershell
cd d:\VALClean\backend
.\venv\Scripts\python.exe manage.py shell
```

Then:
```python
from django.core.mail import send_mail

send_mail(
    subject='Test Email from VALClean',
    message='This is a test email to verify Gmail configuration.',
    from_email='dommovoy@gmail.com',
    recipient_list=['dommovoy@gmail.com'],  # Send to yourself
    fail_silently=False,
)
```

**Expected:** Email arrives in your Gmail inbox.

---

## 🎯 What This Enables

- ✅ Booking confirmation emails (sent when order confirmed)
- ✅ Booking reminder emails (24h before appointment)
- ✅ Booking cancellation emails (when order cancelled)

**Emails sent automatically** when orders are confirmed!
