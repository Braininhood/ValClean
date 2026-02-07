# ✅ Setup Complete - Frontend & Backend

## ✅ Status: ALL DEPENDENCIES INSTALLED & CONFIGURED

### 1. ✅ Backend Setup Complete

**Environment:**
- ✅ Virtual environment created: `backend/venv/`
- ✅ All Python dependencies installed
- ✅ `.env` file created with SECRET_KEY
- ✅ Django settings configured
- ✅ SQLite database configured for development

**Installed Packages:**
- ✅ Django 5.0.0
- ✅ Django REST Framework 3.14.0
- ✅ JWT Authentication
- ✅ CORS Headers
- ✅ API Documentation (drf-spectacular)
- ✅ All other dependencies

**Note:** 
- Custom User model (`accounts.User`) will be created in Week 1 Day 5
- Currently using Django's default User model temporarily
- Database migrations will be created after models are implemented

### 2. ✅ Frontend Setup Complete

**Environment:**
- ✅ `.env.local` file created
- ✅ Next.js 14+ configured
- ✅ TypeScript configured
- ✅ Tailwind CSS configured
- ✅ All npm dependencies installed

**Installed Packages:**
- ✅ Next.js 14.0
- ✅ React 18.2
- ✅ TypeScript 5.3
- ✅ Tailwind CSS 3.3.6
- ✅ All other dependencies (axios, zustand, react-hook-form, etc.)

**Configuration:**
- ✅ API URL: `http://localhost:8000/api`
- ✅ Frontend URL: `http://localhost:3000`
- ✅ CORS configured for frontend-backend communication

---

## 🚀 Starting Both Servers

### Option 1: Start Servers Separately (Recommended)

**Terminal 1 - Backend (Django):**
```bash
cd backend
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# or
source venv/bin/activate     # Linux/Mac

python manage.py runserver
```
Backend will run at: `http://localhost:8000`

**Terminal 2 - Frontend (Next.js):**
```bash
cd frontend
npm run dev
```
Frontend will run at: `http://localhost:3000`

### Option 2: Start Both with PowerShell Script (RECOMMENDED)

Use the provided `start-dev.ps1` script in the root directory:

**Start both servers:**
```powershell
.\start-dev.ps1
```

**Stop both servers:**
```powershell
.\stop-dev.ps1
```

The `start-dev.ps1` script will:
- ✅ Check if directories exist
- ✅ Check if virtual environment exists
- ✅ Check if node_modules exists (installs if missing)
- ✅ Stop any existing servers on ports 8000 and 3000
- ✅ Start backend server in a new PowerShell window
- ✅ Wait 3 seconds for backend to start
- ✅ Start frontend server in a new PowerShell window
- ✅ Display all URLs and information

Two separate PowerShell windows will open - one for backend and one for frontend.
To stop servers, press `Ctrl+C` in each window, or run `.\stop-dev.ps1`.

---

## ✅ Verification Checklist

### Backend Verification:
- [x] Virtual environment exists: `backend/venv/`
- [x] Dependencies installed
- [x] `.env` file created with SECRET_KEY
- [x] Django settings configured
- [x] Database migrations (created and applied in Week 1 Day 5)
- [x] Admin superuser (created with all models)

### Frontend Verification:
- [x] Node modules installed: `frontend/node_modules/`
- [x] `.env.local` file created
- [x] Next.js configured
- [x] TypeScript configured
- [x] Tailwind CSS configured

---

## 📋 Next Steps

### ✅ Week 1 Day 5: Database Models - COMPLETE
- ✅ User and Profile models created (with roles and calendar sync)
- ✅ Manager model created (with flexible permissions)
- ✅ Service and Category models created
- ✅ Staff, StaffSchedule, StaffService, StaffArea models created
- ✅ Customer and Address models created
- ✅ Appointment and CustomerAppointment models created (with calendar sync)
- ✅ Subscription and SubscriptionAppointment models created (guest checkout support)
- ✅ Order and OrderItem models created (guest checkout support)
- ✅ `AUTH_USER_MODEL = 'accounts.User'` enabled in settings
- ✅ All migrations created and applied
- ✅ Superuser created (username: `admin`, password: `admin123`)

### Week 2: Authentication System
1. Implement authentication endpoints (backend)
2. Implement authentication UI (frontend)
3. Test login/registration flow

---

## 🔧 Troubleshooting

### Backend Issues:

**Issue:** `AUTH_USER_MODEL refers to model 'accounts.User' that has not been installed`
**Solution:** This is expected. Custom User model will be created in Week 1 Day 5. For now, using default User model (commented out in settings).

**Issue:** `ModuleNotFoundError: No module named 'django'`
**Solution:** Activate virtual environment first:
```bash
cd backend
.\venv\Scripts\Activate.ps1  # Windows
```

**Issue:** Database connection errors
**Solution:** SQLite database will be created automatically on first migration.

### Frontend Issues:

**Issue:** `Module not found` errors
**Solution:** Install dependencies:
```bash
cd frontend
npm install
```

**Issue:** API connection errors
**Solution:** 
1. Check backend is running on `http://localhost:8000`
2. Check `.env.local` has correct `NEXT_PUBLIC_API_URL`
3. Check CORS settings in backend

---

## 📝 Environment Files

### Backend `.env` (backend/.env):
```
SECRET_KEY=... (generated)
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend `.env.local` (frontend/.env.local):
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_API_VERSION=v1
NEXT_PUBLIC_APP_NAME=VALClean Booking System
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

---

## 🔐 Admin Access (Development)

**Admin Panel:** http://localhost:8000/admin/

**Credentials:**
- **Username:** `admin`
- **Email:** `admin@valclean.uk`
- **Password:** `admin123`
- **Role:** `admin`

**Note:** These are development credentials. **Change the password in production!**

---

## ✅ Setup Status

**Backend:** ✅ Ready (all models created and migrated)
**Frontend:** ✅ Ready
**Dependencies:** ✅ All installed
**Configuration:** ✅ Complete
**Database:** ✅ SQLite initialized with all models
**Admin Panel:** ✅ Accessible with credentials above
**Servers:** ✅ Ready to start

Both frontend and backend are ready to work together! 🎉
