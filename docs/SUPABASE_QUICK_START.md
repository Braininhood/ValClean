# Supabase Quick Start Guide

This is a condensed version of the full migration guide. Use this for quick reference.

## 🚀 Quick Setup (5 Steps)

### 1. Create Supabase Project
1. Go to https://app.supabase.com
2. Create new project
3. Save credentials from **Settings → API**:
   - Project URL
   - anon/public key
   - service_role key

### 2. Install Dependencies

**Backend:**
```powershell
cd backend
.\venv\Scripts\activate
pip install supabase psycopg2-binary dj-database-url
```

**Frontend:**
```powershell
cd frontend
npm install @supabase/supabase-js
```

### 3. Configure Environment Variables

**Backend** (`backend/.env`):
```env
# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres
```

**Frontend** (`frontend/.env.local`):
```env
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...
```

### 4. Update Django Settings

**File**: `backend/config/settings/base.py`

Add Supabase settings:
```python
# Supabase Configuration
SUPABASE_URL = env('SUPABASE_URL', default='')
SUPABASE_ANON_KEY = env('SUPABASE_ANON_KEY', default='')
SUPABASE_SERVICE_ROLE_KEY = env('SUPABASE_SERVICE_ROLE_KEY', default='')
```

Update database (if using Supabase):
```python
import dj_database_url

database_url = env('DATABASE_URL', default=None)
if database_url and database_url.startswith('postgresql://'):
    DATABASES = {
        'default': dj_database_url.config(
            default=database_url,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
```

### 5. Create Storage Buckets

In Supabase Dashboard → **Storage**:
- Create buckets: `avatars`, `services`, `staff`, `categories`, `appointment-photos`
- Set public buckets to public read access

## 📝 Files Already Created

The following files have been created for you:

### Backend:
- ✅ `backend/apps/core/supabase_auth.py` - Authentication service
- ✅ `backend/apps/core/supabase_storage.py` - Storage service
- ✅ `backend/apps/core/storage_backend.py` - Django storage backend
- ✅ `backend/apps/core/views.py` - File upload endpoint

### Frontend:
- ✅ `frontend/lib/supabase/client.ts` - Supabase client
- ✅ `frontend/hooks/use-supabase-auth.ts` - Auth hook

## 🔄 Migration Options

### Option 1: Full Migration (Recommended)
Follow the complete guide in `SUPABASE_MIGRATION_GUIDE.md`

### Option 2: Gradual Migration
1. **Start with Database**: Migrate to Supabase PostgreSQL first
2. **Then Storage**: Move file uploads to Supabase Storage
3. **Finally Auth**: Switch authentication to Supabase Auth

### Option 3: Hybrid Approach
- Keep Django auth for now
- Use Supabase for database and storage only
- Migrate auth later

## 🧪 Testing

### Test Database Connection:
```powershell
cd backend
python manage.py dbshell
```

### Test Authentication:
```powershell
# Register
curl -X POST http://localhost:8000/api/aut/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123456","name":"Test User"}'
```

### Test File Upload:
```powershell
curl -X POST http://localhost:8000/api/core/upload/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.jpg" \
  -F "bucket=avatars"
```

## 📚 Next Steps

1. Read the full guide: `SUPABASE_MIGRATION_GUIDE.md`
2. Test each component individually
3. Migrate data using the migration script
4. Update frontend to use Supabase auth hook
5. Deploy to production

## 🆘 Common Issues

**Database Connection Error:**
- Add `'OPTIONS': {'sslmode': 'require'}` to database config

**Authentication Not Working:**
- Verify SUPABASE_ANON_KEY is correct
- Check Supabase Dashboard → Authentication → Settings

**File Upload Fails:**
- Create buckets in Supabase Dashboard
- Check bucket policies (public vs private)

## 📖 Full Documentation

See `SUPABASE_MIGRATION_GUIDE.md` for complete step-by-step instructions.
