# Database Setup Guide

## 📊 Database Configuration

Your Django application is configured to use **different databases** depending on the environment:

### 🏠 Local Development (localhost)
- **Database**: SQLite
- **File**: `db.sqlite3` (created automatically in your project folder)
- **Installation**: ✅ **No installation needed!** SQLite comes with Python
- **When**: When `DATABASE_URL` environment variable is **NOT set**

### 🌐 Production (Render - valclean.onrender.com)
- **Database**: PostgreSQL
- **Installation**: ✅ **No installation needed!** Render provides it automatically
- **When**: When `DATABASE_URL` environment variable **IS set** (by Render)

---

## 🚀 Setting Up PostgreSQL on Render

### Step 1: Create PostgreSQL Database

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** button (top right)
3. Select **"PostgreSQL"**
4. Configure:
   - **Name**: `valclean-db` (or any name you prefer)
   - **Database**: `valclean` (or leave default)
   - **User**: `valclean_user` (or leave default)
   - **Region**: Choose closest to you
   - **Plan**: Free (or paid if you need more)
5. Click **"Create Database"**
6. Wait for it to be created (takes 1-2 minutes)

### Step 2: Link Database to Your Web Service

1. Go to your **Web Service** (the Django app)
2. Go to **"Settings"** tab
3. Scroll down to **"Environment"** section
4. Find **"Add Environment Variable"**
5. You'll see a section for **"Add from Database"** or similar
6. Select your PostgreSQL database from the dropdown
7. Render will automatically add `DATABASE_URL` environment variable

**OR** manually add:
- **Key**: `DATABASE_URL`
- **Value**: Copy the **Internal Database URL** from your PostgreSQL service

### Step 3: Verify Database Connection

After linking, your web service will automatically:
- Use PostgreSQL instead of SQLite
- Connect to the database using the `DATABASE_URL`
- No additional configuration needed!

---

## 📝 How It Works

### In `config/settings.py`:

```python
# Check if DATABASE_URL is set
if DATABASE_URL:
    # Production: Use PostgreSQL (from Render)
    DATABASES = {
        'default': dj_database_url.config(...)  # PostgreSQL
    }
else:
    # Development: Use SQLite (local)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',  # SQLite file
        }
    }
```

### What This Means:

- **On Render**: `DATABASE_URL` is automatically set → Uses PostgreSQL ✅
- **On localhost**: `DATABASE_URL` is not set → Uses SQLite ✅

---

## 🔄 Running Migrations

### On Render (PostgreSQL):

1. Open **Render Shell** (see `HOW_TO_ACCESS_RENDER_SHELL.md`)
2. Run:
   ```bash
   python manage.py migrate
   ```
3. This creates all tables in **PostgreSQL** (not SQLite!)

### On Localhost (SQLite):

1. Open terminal in your project folder
2. Run:
   ```bash
   python manage.py migrate
   ```
3. This creates `db.sqlite3` file in your project folder

---

## ✅ Summary

| Environment | Database | Installation Needed? | File/Location |
|------------|----------|---------------------|---------------|
| **Localhost** | SQLite | ❌ No (comes with Python) | `db.sqlite3` in project folder |
| **Render** | PostgreSQL | ❌ No (provided by Render) | Managed by Render |

### What You Need to Do:

1. ✅ **On Render**: Create PostgreSQL database service and link it to your web service
2. ✅ **On localhost**: Nothing! SQLite works automatically
3. ✅ **Run migrations**: On both environments after setup

---

## 🆘 Troubleshooting

### "No such table" error on Render
- Make sure you've run `python manage.py migrate` in Render Shell
- Verify `DATABASE_URL` is set in environment variables
- Check that database is linked to your web service

### SQLite file not created locally
- Make sure you're running migrations: `python manage.py migrate`
- Check file permissions in your project folder
- Verify `DATABASE_URL` is NOT set in your local environment

### Database connection error on Render
- Verify PostgreSQL service is running (green status)
- Check `DATABASE_URL` is correctly set
- Make sure database is linked to your web service

---

## 📚 Additional Notes

- **SQLite** is perfect for development (simple, no setup)
- **PostgreSQL** is required for production (better performance, features)
- Both databases use the **same Django models** - no code changes needed!
- Migrations work the same way on both databases

---

**You don't need to install anything!** 
- SQLite comes with Python ✅
- PostgreSQL is provided by Render ✅

Just create the PostgreSQL service on Render and link it to your web service! 🚀

