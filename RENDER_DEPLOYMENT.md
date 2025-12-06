# Render Deployment Configuration for ValClean

## 🚀 Quick Setup Guide

### 1. Environment Variables in Render Dashboard

Go to your Render service → Environment tab and add these variables:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here-generate-with-django-admin
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,valclean.onrender.com

# Database (Auto-provided by Render PostgreSQL)
DATABASE_URL=<automatically-set-by-render>

# Optional: Redis (if you add Redis service)
REDIS_URL=redis://your-redis-url:6379/0
CELERY_BROKER_URL=redis://your-redis-url:6379/0
CELERY_RESULT_BACKEND=redis://your-redis-url:6379/0

# Payment Gateways (Optional - add when ready)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
PAYPAL_CLIENT_ID=...
PAYPAL_CLIENT_SECRET=...

# Email (Optional - add when ready)
EMAIL_BACKEND=django_sendgrid_v5.backends.SendgridBackend
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@valclean.com

# SMS (Optional - add when ready)
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=...
```

### 2. Build & Start Commands

**Build Command:**
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

**Start Command:**
```bash
gunicorn config.wsgi:application
```

### 3. After First Deployment

Once deployed, you need to run migrations and create a superuser:

1. Go to Render Dashboard → Your Service → Shell
2. Run:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

### 4. Update Site Domain

After deployment, update the Site framework domain:

1. Go to Shell in Render Dashboard
2. Run:
   ```bash
   python manage.py shell
   ```
3. Execute:
   ```python
   from django.contrib.sites.models import Site
   site = Site.objects.get_current()
   site.domain = 'valclean.onrender.com'
   site.name = 'ValClean Booking System'
   site.save()
   ```

### 5. Access Your Application

- **Production**: https://valclean.onrender.com
- **Local Development**: http://localhost:8000

---

## 🔧 Configuration Details

### Allowed Hosts
The application is configured to accept requests from:
- `localhost` (for local development)
- `127.0.0.1` (for local development)
- `valclean.onrender.com` (for production on Render)

### Database
- **Production**: PostgreSQL (automatically configured via `DATABASE_URL`)
- **Development**: SQLite (when `DATABASE_URL` is not set)

### Static Files
- Served by WhiteNoise in production
- Automatically collected during build process

### HTTPS
- Automatically enforced in production (when `DEBUG=False`)
- Disabled in development for local testing

---

## 📝 Notes

1. **Free Tier**: Render's free tier spins down after 15 minutes of inactivity. First request after spin-down may take 30-60 seconds.

2. **Database**: PostgreSQL is automatically provided by Render. The `DATABASE_URL` is set automatically - you don't need to configure it manually.

3. **Static Files**: WhiteNoise serves static files directly from Django, so no separate static file service is needed.

4. **Environment Variables**: Make sure to set `DEBUG=False` in production for security.

5. **Secret Key**: Generate a new secret key for production:
   ```python
   from django.core.management.utils import get_random_secret_key
   print(get_random_secret_key())
   ```

---

## 🐛 Troubleshooting

### Build Fails
- Check that all dependencies in `requirements.txt` are valid
- Verify Python version compatibility

### 500 Internal Server Error
- Check Render logs for detailed error messages
- Verify all environment variables are set
- Make sure migrations have been run

### Static Files Not Loading
- Verify `collectstatic` ran successfully during build
- Check WhiteNoise is in `MIDDLEWARE`
- Ensure `STATIC_ROOT` is set correctly

### Database Connection Error
- Verify `DATABASE_URL` is set (should be automatic)
- Check PostgreSQL service is running in Render

---

## 🔗 Useful Links

- [Render Dashboard](https://dashboard.render.com)
- [Render Django Docs](https://render.com/docs/deploy-django)
- Your App: https://valclean.onrender.com

