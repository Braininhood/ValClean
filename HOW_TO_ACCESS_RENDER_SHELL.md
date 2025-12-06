# How to Access Render Shell - Step by Step Guide

## 📍 Step-by-Step Instructions

### Method 1: Through Render Dashboard (Easiest)

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Log in with your account

2. **Find Your Service**
   - You'll see a list of your services (databases, web services, etc.)
   - Click on your **Web Service** (the one running your Django app)
   - It might be named something like:
     - `booking-system`
     - `valclean`
     - Or whatever name you gave it

3. **Open the Shell**
   - Once you're on your service page, look at the **left sidebar**
   - You'll see menu items like:
     - Overview
     - Logs
     - **Shell** ← Click this!
     - Settings
     - Environment
     - etc.

4. **Use the Terminal**
   - A terminal window will open in your browser
   - You can now type commands directly
   - It's like a command prompt/terminal, but running on Render's servers

---

## 🖼️ Visual Guide

```
Render Dashboard
├── Services List
│   └── [Your Web Service] ← Click here
│       ├── Overview
│       ├── Logs
│       ├── Shell ← Click here to open terminal!
│       ├── Settings
│       └── Environment
```

---

## 💻 Common Commands to Run in Shell

Once you have the Shell open, you can run Django commands:

### Run Migrations
```bash
python manage.py migrate
```

### Create Superuser
```bash
python manage.py createsuperuser
```
(It will prompt you for username, email, and password)

### Update Site Domain
```bash
python manage.py shell
```
Then in the Python shell:
```python
from django.contrib.sites.models import Site
site = Site.objects.get_current()
site.domain = 'valclean.onrender.com'
site.name = 'ValClean Booking System'
site.save()
exit()
```

### Check Django Version
```bash
python -m django --version
```

### List Installed Packages
```bash
pip list
```

---

## 🔍 Alternative: If You Don't See "Shell" Option

If you don't see a "Shell" option in the sidebar:

1. **Check Service Type**: Make sure you're looking at a **Web Service**, not a Database or other service type
2. **Check Permissions**: Make sure you have the right permissions for the service
3. **Try Different Browser**: Sometimes browser extensions can hide menu items
4. **Use Render CLI** (see Method 2 below)

---

## 🖥️ Method 2: Using Render CLI (Command Line)

If you prefer using your local terminal:

1. **Install Render CLI**
   ```bash
   npm install -g render-cli
   ```
   (Requires Node.js to be installed)

2. **Login to Render**
   ```bash
   render login
   ```
   (This will open a browser for authentication)

3. **Connect to Shell**
   ```bash
   render shell --service your-service-name
   ```
   Replace `your-service-name` with your actual service name

4. **Run Commands**
   - Now you can run Django commands as if you're on the server

---

## ⚠️ Important Notes

- **Shell Access**: The Shell runs commands directly on your Render service
- **Environment**: All environment variables you set in Render are available in the Shell
- **Working Directory**: You'll be in your project's root directory
- **Python Path**: Python and Django are already installed and configured
- **Database**: The database connection is already configured via `DATABASE_URL`

---

## 🆘 Troubleshooting

### "Shell" option is missing
- Make sure you're viewing a **Web Service**, not a Database
- Try refreshing the page
- Check if your service is still deploying (wait for it to finish)

### Commands not working
- Make sure your service has finished deploying
- Check that Python is available: `python --version`
- Verify you're in the right directory: `pwd`

### Can't connect via CLI
- Make sure you're logged in: `render whoami`
- Verify the service name is correct
- Check that Render CLI is up to date

---

## 📚 Quick Reference

**Direct Links:**
- Render Dashboard: https://dashboard.render.com
- Render Docs: https://render.com/docs
- Your App: https://valclean.onrender.com

**Most Common First-Time Commands:**
```bash
# 1. Run migrations
python manage.py migrate

# 2. Create admin user
python manage.py createsuperuser

# 3. Update site domain
python manage.py shell
# Then in Python shell:
from django.contrib.sites.models import Site
site = Site.objects.get_current()
site.domain = 'valclean.onrender.com'
site.name = 'ValClean Booking System'
site.save()
exit()
```

That's it! You're ready to manage your Django app on Render! 🚀

