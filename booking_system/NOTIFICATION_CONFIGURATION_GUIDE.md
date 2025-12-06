# Notification System Configuration Guide

This guide provides step-by-step instructions for configuring Email, SMS (Twilio), and Celery for the notification system.

---

## 📧 Email Configuration

### Option 1: SendGrid (Recommended)

**Step 1: Create SendGrid Account**
1. Go to https://sendgrid.com
2. Click "Start for Free" and create an account
3. Verify your email address
4. Complete the account setup

**Step 2: Create API Key**
1. Log in to SendGrid Dashboard
2. Go to **Settings** → **API Keys**
3. Click **Create API Key**
4. Name it (e.g., "Booking System")
5. Select **Full Access** or **Restricted Access** (Mail Send permission)
6. Click **Create & View**
7. **Copy the API key immediately** (you won't see it again!)

**Step 3: Configure Django Settings**

Add to your `.env` file (in project root):
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.your_actual_api_key_here
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

**Important Notes:**
- Replace `SG.your_actual_api_key_here` with your actual SendGrid API key
- Replace `noreply@yourdomain.com` with your verified sender email
- In SendGrid, you need to verify your sender email/domain first

**Step 4: Verify Sender Email (SendGrid)**
1. Go to **Settings** → **Sender Authentication**
2. Click **Verify a Single Sender**
3. Fill in the form and verify via email
4. Use this verified email in `DEFAULT_FROM_EMAIL`

### Option 2: Gmail SMTP

**Step 1: Enable App Password**
1. Go to your Google Account: https://myaccount.google.com
2. Go to **Security** → **2-Step Verification** (enable if not enabled)
3. Go to **Security** → **App passwords**
4. Select **Mail** and **Other (Custom name)**
5. Name it "Django Booking System"
6. Click **Generate**
7. **Copy the 16-character password**

**Step 2: Configure Django Settings**

Add to your `.env` file:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_16_character_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com
```

### Option 3: Other SMTP Providers

**For Mailgun:**
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=postmaster@yourdomain.mailgun.org
EMAIL_HOST_PASSWORD=your_mailgun_password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

**For AWS SES:**
```env
EMAIL_BACKEND=django_ses.SESBackend
AWS_SES_REGION_NAME=us-east-1
AWS_SES_REGION_ENDPOINT=email.us-east-1.amazonaws.com
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### Testing Email Configuration

After configuration, test it:

```bash
python manage.py shell
```

```python
from django.core.mail import send_mail

send_mail(
    'Test Email',
    'This is a test email from the booking system.',
    'noreply@yourdomain.com',
    ['your_test_email@example.com'],
    fail_silently=False,
)
```

If successful, you'll see the email in your inbox!

---

## 📱 SMS Configuration (Twilio)

### Step 1: Create Twilio Account

1. Go to https://www.twilio.com
2. Click **Sign Up** (free trial available)
3. Fill in the registration form:
   - Email address
   - Password
   - Full name
   - Phone number (for verification)
4. Verify your email and phone number
5. Complete the account setup

### Step 2: Get Your Credentials

1. Log in to Twilio Console: https://console.twilio.com
2. You'll see your **Account SID** and **Auth Token** on the dashboard
3. **Copy both values** (keep them secure!)

**Account SID:** Starts with `AC...` (e.g., `AC[YOUR_TWILIO_ACCOUNT_SID]`)
**Auth Token:** Long string (e.g., `your_auth_token_here`)

### Step 3: Get a Phone Number

1. In Twilio Console, go to **Phone Numbers** → **Manage** → **Buy a number**
2. Select your country (e.g., United States)
3. For testing, select **Voice & SMS** capability
4. Click **Search**
5. Choose a number and click **Buy**
6. **Copy the phone number** (e.g., `+1234567890`)

**Note:** Free trial accounts get a trial number. For production, you'll need to upgrade.

### Step 4: Install Twilio Python Library

```bash
pip install twilio
```

Or add to `requirements.txt`:
```
twilio>=8.10.0
```

### Step 5: Configure Django Settings

Add to your `.env` file:
```env
TWILIO_ACCOUNT_SID=AC[YOUR_TWILIO_ACCOUNT_SID]
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
```

**Important:**
- Replace with your actual Account SID (starts with `AC`)
- Replace with your actual Auth Token
- Replace with your Twilio phone number (include `+` and country code)

### Step 6: Verify Phone Numbers (Free Trial)

**Important for Free Trial:**
- Twilio free trial can only send SMS to **verified phone numbers**
- Go to **Phone Numbers** → **Manage** → **Verified Caller IDs**
- Add phone numbers you want to send SMS to
- Verify them via phone call or SMS

### Testing SMS Configuration

After configuration, test it:

```bash
python manage.py shell
```

```python
from notifications.services import SMSNotificationService

sms_service = SMSNotificationService()
result = sms_service.send_sms(
    recipient_phone='+1234567890',  # Your verified phone number
    message='Test SMS from booking system'
)

print(result)
# Should show: {'success': True, 'message_sid': 'SM...', 'status': 'queued'}
```

---

## ⏰ Celery Configuration (For Reminder System)

### Why Celery is Needed

Celery is required for:
- **Reminder notifications** (send X hours before appointment)
- **Follow-up notifications** (send after appointment completes)
- **Retry failed notifications**
- **Background task processing**

Without Celery, these features won't work automatically.

### Step 1: Install Redis (Message Broker)

**Windows:**
1. Download Redis for Windows: https://github.com/microsoftarchive/redis/releases
2. Or use WSL (Windows Subsystem for Linux)
3. Or use Docker: `docker run -d -p 6379:6379 redis`

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Start Redis
redis-server
```

**Verify Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

### Step 2: Install Celery

```bash
pip install celery redis
```

Or ensure these are in `requirements.txt`:
```
celery>=5.3.0
redis>=5.0.0
django-celery-beat>=2.5.0
```

### Step 3: Configure Celery

Celery is already configured in `config/settings.py`. Verify these settings:

```python
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
```

Add to `.env` (optional, defaults are fine):
```env
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Step 4: Create Celery Configuration File

Create `config/celery.py` (if not exists):

```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('booking_system')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

### Step 5: Update `config/__init__.py`

Ensure `config/__init__.py` includes:

```python
from .celery import app as celery_app

__all__ = ('celery_app',)
```

### Step 6: Start Celery Worker

Open a **new terminal window** and run:

```bash
cd D:\VALClean\booking_system
celery -A config worker --loglevel=info
```

You should see:
```
[INFO/MainProcess] Connected to redis://localhost:6379/0
[INFO/MainProcess] celery@hostname ready.
```

**Keep this terminal open!** The worker needs to run continuously.

### Step 7: Start Celery Beat (For Periodic Tasks)

Open **another terminal window** and run:

```bash
cd D:\VALClean\booking_system
celery -A config beat --loglevel=info
```

You should see:
```
[INFO/MainProcess] beat: Starting...
[INFO/MainProcess] Scheduler: Sending due task notifications.tasks.send_appointment_reminders
```

**Keep this terminal open too!**

### Step 8: Configure Periodic Tasks

**Option A: Using Django Admin (Recommended)**

1. Install django-celery-beat (if not already):
   ```bash
   pip install django-celery-beat
   ```

2. Add to `INSTALLED_APPS` in `settings.py`:
   ```python
   'django_celery_beat',
   ```

3. Run migrations:
   ```bash
   python manage.py migrate django_celery_beat
   ```

4. Go to Django Admin → **Periodic Tasks**
5. Create new periodic tasks:
   - **Task:** `notifications.tasks.send_appointment_reminders`
   - **Interval:** Every 1 hour
   - **Enabled:** Yes

   - **Task:** `notifications.tasks.send_follow_up_notifications`
   - **Interval:** Every 6 hours
   - **Enabled:** Yes

**Option B: Using Code (Alternative)**

Create `config/celery.py` with periodic tasks:

```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    'send-appointment-reminders': {
        'task': 'notifications.tasks.send_appointment_reminders',
        'schedule': crontab(minute=0),  # Every hour
    },
    'send-follow-up-notifications': {
        'task': 'notifications.tasks.send_follow_up_notifications',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
    },
    'retry-failed-notifications': {
        'task': 'notifications.tasks.retry_failed_notifications',
        'schedule': crontab(minute=0, hour='*/12'),  # Every 12 hours
    },
}
```

### Step 9: Testing Celery

Test that Celery is working:

```bash
python manage.py shell
```

```python
from notifications.tasks import send_appointment_reminders

# Run task manually
result = send_appointment_reminders.delay()
print(result.get())  # Should show: {'sent': X, 'errors': Y}
```

### Running Celery in Production

**For production, use a process manager like Supervisor or systemd:**

**Supervisor example (`/etc/supervisor/conf.d/celery.conf`):**
```ini
[program:celery_worker]
command=/path/to/venv/bin/celery -A config worker --loglevel=info
directory=/path/to/booking_system
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/worker.log

[program:celery_beat]
command=/path/to/venv/bin/celery -A config beat --loglevel=info
directory=/path/to/booking_system
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/beat.log
```

---

## 🚀 Quick Setup Summary

### 1. Email (SendGrid - 5 minutes)
- [ ] Sign up at sendgrid.com
- [ ] Create API key
- [ ] Verify sender email
- [ ] Add to `.env` file
- [ ] Test email sending

### 2. SMS (Twilio - 10 minutes)
- [ ] Sign up at twilio.com
- [ ] Get Account SID and Auth Token
- [ ] Buy/Get phone number
- [ ] Install: `pip install twilio`
- [ ] Add to `.env` file
- [ ] Verify test phone numbers
- [ ] Test SMS sending

### 3. Celery (15 minutes)
- [ ] Install Redis (or use Docker)
- [ ] Install: `pip install celery redis django-celery-beat`
- [ ] Start Redis: `redis-server`
- [ ] Start Celery Worker: `celery -A config worker --loglevel=info`
- [ ] Start Celery Beat: `celery -A config beat --loglevel=info`
- [ ] Configure periodic tasks in Django Admin
- [ ] Test reminder system

---

## 📝 Complete `.env` File Example

```env
# Email Configuration (SendGrid)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.your_sendgrid_api_key_here
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# SMS Configuration (Twilio)
TWILIO_ACCOUNT_SID=AC[YOUR_TWILIO_ACCOUNT_SID]
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890

# Celery Configuration (Redis)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

---

## ✅ Verification Checklist

After configuration, verify everything works:

- [ ] **Email:** Can send test email via Django shell
- [ ] **SMS:** Can send test SMS via Django shell
- [ ] **Redis:** `redis-cli ping` returns `PONG`
- [ ] **Celery Worker:** Running and connected to Redis
- [ ] **Celery Beat:** Running and scheduling tasks
- [ ] **Notifications:** Create test appointment, verify notifications sent
- [ ] **Reminders:** Create appointment 25 hours in future, verify reminder sent after 1 hour

---

## 🆘 Troubleshooting

### Email Not Sending
- Check `.env` file has correct credentials
- Verify sender email is verified in SendGrid
- Check spam folder
- Check Django logs for errors
- Test with console backend first: `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`

### SMS Not Sending
- Verify Twilio credentials in `.env`
- Check phone number format (must include `+` and country code)
- For free trial, verify recipient phone number in Twilio
- Check Twilio console for error logs
- Verify `twilio` package is installed

### Celery Not Working
- Verify Redis is running: `redis-cli ping`
- Check Celery worker is running (separate terminal)
- Check Celery beat is running (separate terminal)
- Verify Redis connection in Celery logs
- Check Django settings for Celery configuration

---

**Last Updated:** December 2025
**Status:** Complete Configuration Guide

