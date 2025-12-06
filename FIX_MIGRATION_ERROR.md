# Fix: "no such table: accounts_user" Error on Render

## 🔴 The Problem

You're seeing this error:
```
django.db.utils.OperationalError: no such table: accounts_user
```

**This means**: The database tables haven't been created yet. You need to run migrations!

---

## ✅ Solution: Run Migrations on Render

### Step 1: Access Render Shell

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click on your **Web Service** (valclean)
3. Click **"Shell"** in the left sidebar
4. A terminal will open in your browser

### Step 2: Run Migrations

In the Render Shell, run these commands:

```bash
# First, check if you're connected to the right database
python manage.py showmigrations

# Run all migrations to create tables
python manage.py migrate

# Create a superuser (admin account)
python manage.py createsuperuser
```

### Step 3: Verify Tables Were Created

After running migrations, verify:

```bash
# Check if tables exist
python manage.py dbshell
```

Then in the database shell:
```sql
-- For PostgreSQL:
\dt

-- Or check specific table:
SELECT * FROM accounts_user LIMIT 1;
```

Type `\q` to exit the database shell.

---

## 🔍 Additional Checks

### Check 1: Verify DATABASE_URL is Set

In Render Shell, run:
```bash
python manage.py shell
```

Then in Python shell:
```python
from django.conf import settings
print(settings.DATABASES)
exit()
```

You should see PostgreSQL configuration, not SQLite.

### Check 2: Check Which Database is Being Used

The error traceback shows `sqlite3/base.py`, which means it's trying to use SQLite instead of PostgreSQL.

**Fix**: Make sure `DATABASE_URL` is set in Render environment variables:
1. Go to Render Dashboard → Your Web Service → Settings
2. Check **Environment Variables**
3. Verify `DATABASE_URL` is set with your PostgreSQL connection string

---

## 📝 Complete Setup Checklist

- [ ] PostgreSQL database created on Render
- [ ] `DATABASE_URL` environment variable set in Render
- [ ] Web service linked to PostgreSQL database (or DATABASE_URL manually added)
- [ ] Migrations run: `python manage.py migrate`
- [ ] Superuser created: `python manage.py createsuperuser`
- [ ] Site domain updated (if needed)

---

## 🚀 Quick Fix Commands

Copy and paste these into Render Shell:

```bash
# 1. Run migrations
python manage.py migrate

# 2. Create admin user
python manage.py createsuperuser

# 3. Update site domain (optional)
python manage.py shell
```

Then in Python shell:
```python
from django.contrib.sites.models import Site
site = Site.objects.get_current()
site.domain = 'valclean.onrender.com'
site.name = 'ValClean Booking System'
site.save()
exit()
```

---

## 🆘 If Migrations Still Fail

### Error: "relation does not exist"
- Make sure PostgreSQL database is running
- Verify `DATABASE_URL` is correct
- Check database connection

### Error: "permission denied"
- Verify database user has correct permissions
- Check database credentials

### Error: "connection refused"
- Verify PostgreSQL service is running in Render
- Check hostname and port are correct
- Make sure database is linked to web service

---

## 📚 Next Steps After Migrations

Once migrations are successful:

1. **Test Login**: Try logging in with your superuser account
2. **Create Sample Data** (optional):
   ```bash
   python manage.py create_sample_data
   ```
3. **Access Admin Panel**: https://valclean.onrender.com/admin/

---

## ✅ Expected Result

After running migrations, you should see output like:

```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, accounts, ...
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying accounts.0001_initial... OK
  ...
```

Then the login should work! 🎉

