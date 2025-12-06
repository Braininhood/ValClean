# Render Database Configuration

## 🔐 Your PostgreSQL Database Credentials

**Hostname**: `dpg-d4qb2m49c44c73ba23c0-a`  
**Port**: `5432`  
**Database**: `valclean`  
**Username**: `valclean_user`  
**Password**: `WsTALgkx3lH2o8lv8BOgONMKzJ75KDU1`

**⚠️ Important**: The hostname might need the full domain. Check your Render PostgreSQL service for the complete hostname. It's usually something like:
- `dpg-d4qb2m49c44c73ba23c0-a.oregon-postgres.render.com`
- Or similar with your region (oregon, frankfurt, singapore, etc.)

---

## 📝 Step 1: Add DATABASE_URL to Render

### Option A: Using Render Dashboard (Recommended)

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click on your **Web Service** (your Django app)
3. Go to **"Settings"** tab
4. Scroll to **"Environment Variables"** section
5. Click **"Add Environment Variable"**
6. Add:
   - **Key**: `DATABASE_URL`
   - **Value**: `postgresql://valclean_user:WsTALgkx3lH2o8lv8BOgONMKzJ75KDU1@dpg-d4qb2m49c44c73ba23c0-a.oregon-postgres.render.com:5432/valclean`
   
   **⚠️ Important**: 
   - Check your PostgreSQL service in Render → **"Info"** tab → **"Internal Database URL"**
   - Copy the exact hostname from there
   - It might be: `dpg-d4qb2m49c44c73ba23c0-a.oregon-postgres.render.com` or similar
   - Replace `oregon-postgres` with your actual region if different

7. Click **"Save Changes"**
8. Your service will automatically redeploy

### Option B: Link Database Service (Easier - Recommended)

1. Go to your **Web Service** → **Settings**
2. Scroll to **"Add from Database"** section
3. Select your PostgreSQL database from the dropdown
4. Render will automatically add `DATABASE_URL` with the correct connection string
5. No need to manually enter credentials!

---

## 🏠 Step 2: Configure Localhost

You have **3 options** for localhost:

### Option 1: Use SQLite (Recommended for Development) ✅

**Easiest option** - No setup needed!

1. **Don't set** `DATABASE_URL` in your local `.env` file
2. Django will automatically use SQLite
3. Database file: `db.sqlite3` in your project folder

**Pros:**
- ✅ No installation needed
- ✅ Fast for development
- ✅ No network dependency

**Cons:**
- ⚠️ Different database than production (but same models)

### Option 2: Use Same Render Database (Same as Production) ✅

**Connect localhost to Render PostgreSQL (same database):**

1. Create `.env` file in your project root (if it doesn't exist):
   ```bash
   DATABASE_URL=postgresql://valclean_user:WsTALgkx3lH2o8lv8BOgONMKzJ75KDU1@dpg-d4qb2m49c44c73ba23c0-a.oregon-postgres.render.com:5432/valclean
   ```

2. **Important**: Get the full hostname from Render:
   - Go to Render Dashboard → Your PostgreSQL service
   - Click **"Info"** tab
   - Look for **"Internal Database URL"** 
   - Copy the hostname (it should include the full domain)
   - Example: `dpg-d4qb2m49c44c73ba23c0-a.oregon-postgres.render.com`
   - Replace in the connection string above

3. **Note**: The `.env` file is already in `.gitignore`, so your credentials won't be committed to Git

**Pros:**
- ✅ Same database as production
- ✅ No local database setup

**Cons:**
- ⚠️ Requires internet connection
- ⚠️ Slower (network latency)
- ⚠️ Risk of affecting production data
- ⚠️ Free tier database might have connection limits

### Option 3: Install Local PostgreSQL (Advanced)

**Set up PostgreSQL on your computer:**

1. **Install PostgreSQL**:
   - Windows: Download from [postgresql.org](https://www.postgresql.org/download/windows/)
   - Or use: `choco install postgresql` (if you have Chocolatey)

2. **Create database**:
   ```bash
   createdb valclean
   ```

3. **Create `.env` file**:
   ```bash
   DATABASE_URL=postgresql://postgres:your-local-password@localhost:5432/valclean
   ```

**Pros:**
- ✅ Same database type as production
- ✅ Fast (local)
- ✅ No network dependency

**Cons:**
- ⚠️ Requires PostgreSQL installation
- ⚠️ More setup

---

## 🔧 Connection String Format

The `DATABASE_URL` format is:
```
postgresql://username:password@hostname:port/database
```

For your Render database:
```
postgresql://valclean_user:WsTALgkx3lH2o8lv8BOgONMKzJ75KDU1@dpg-d4qb2m49c44c73ba23c0-a.oregon-postgres.render.com:5432/valclean
```

**Important**: 
- Replace `oregon-postgres.render.com` with your actual region
- Check your PostgreSQL service in Render for the exact hostname
- The hostname might be: `dpg-d4qb2m49c44c73ba23c0-a.oregon-postgres.render.com` or similar

---

## ✅ Recommended Setup

### For Production (Render):
- ✅ Use PostgreSQL (via `DATABASE_URL` from Render)
- ✅ Link database service to web service (automatic)

### For Development (Localhost):
- ✅ Use SQLite (no `DATABASE_URL` needed)
- ✅ Fast, simple, no setup

**Why different databases?**
- SQLite is perfect for development (simple, fast)
- PostgreSQL is required for production (better performance, features)
- Django models work the same on both!

---

## 🧪 Testing Connection

### On Render:
1. Open Render Shell
2. Run:
   ```bash
   python manage.py dbshell
   ```
3. If connected, you'll see PostgreSQL prompt

### On Localhost:
1. Open terminal
2. Run:
   ```bash
   python manage.py dbshell
   ```
3. If using SQLite, you'll see SQLite prompt
4. If using PostgreSQL, you'll see PostgreSQL prompt

---

## 🆘 Troubleshooting

### "Connection refused" error
- Check hostname is correct (include full domain)
- Verify database is running in Render
- Check firewall/network settings

### "Authentication failed"
- Verify username and password are correct
- Check password doesn't have special characters that need encoding
- Try regenerating password in Render

### "Database does not exist"
- Verify database name is `valclean`
- Check database was created successfully

---

## 🔒 Security Notes

⚠️ **Important**: 
- Never commit `.env` file to Git (it's in `.gitignore`)
- Never share database credentials publicly
- Use different passwords for production and development
- Rotate passwords regularly

---

## 📚 Quick Reference

**Render DATABASE_URL** (add to Render environment variables):
```
postgresql://valclean_user:WsTALgkx3lH2o8lv8BOgONMKzJ75KDU1@dpg-d4qb2m49c44c73ba23c0-a.oregon-postgres.render.com:5432/valclean
```

**Localhost** (recommended - no DATABASE_URL):
- Just use SQLite (automatic)

**Localhost** (if you want PostgreSQL):
- Install PostgreSQL locally OR
- Connect to Render database (not recommended)

---

**Next Steps:**
1. Add `DATABASE_URL` to Render environment variables
2. Keep localhost using SQLite (no changes needed)
3. Run migrations on Render: `python manage.py migrate`
4. Run migrations locally: `python manage.py migrate`

Done! 🚀

