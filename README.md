# VALClean Booking System - Best Professional Solution

A comprehensive, best-in-class appointment booking system combining the best features from HouseCallPro and Bookly, specifically designed for VALClean (https://valclean.uk/).

## 🎯 New Professional Solution Documents

**Start here for the complete professional solution:**

1. **📘 [SOLUTION_OVERVIEW.md](SOLUTION_OVERVIEW.md)** - Quick start guide and overview
2. **⭐ [VALCLEAN_BEST_SOLUTION.md](VALCLEAN_BEST_SOLUTION.md)** - Complete professional solution (READ THIS FIRST!)
3. **🗺️ [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)** - Step-by-step implementation guide (15 weeks)
4. **📊 [FEATURE_COMPARISON.md](FEATURE_COMPARISON.md)** - Competitive analysis (HouseCallPro vs Bookly vs Our Solution)
5. **🏗️ [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md)** - Detailed technical architecture

**These documents provide:**
- ✅ Complete solution combining best features from HouseCallPro and Bookly
- ✅ **Technology stack confirmed: Next.js + Django**
- ✅ **Development setup: localhost + SQLite**
- ✅ **User roles: Admin, Manager, Staff, Customer**
- ✅ Step-by-step 15-week implementation roadmap
- ✅ Feature-by-feature competitive analysis
- ✅ Detailed technical architecture
- ✅ User experience design
- ✅ Success metrics and KPIs

---

## Original Project

A comprehensive appointment booking system built with Django, inspired by professional booking platforms.

## Features

### ✅ Implemented (Phase 1 & 2)
- ✅ Multi-step booking workflow (8 steps)
- ✅ Staff and service management (full CRUD)
- ✅ Customer management with address fields
- ✅ Appointment scheduling with time slot calculation
- ✅ Role-based authentication (Admin, Manager, Staff, Customer)
- ✅ Role-based dashboards
- ✅ HTTPS enforcement (production)
- ✅ Session-based booking flow
- ✅ Time slot availability checking
- ✅ Staff schedule management
- ✅ Holiday management
- ✅ Sample data creation command

### 🚧 In Progress / Planned (Phase 3+)
- Payment processing (Stripe, PayPal, and more)
- Email and SMS notifications
- Calendar integration (Google, Outlook, Apple) - All roles can sync
- Custom event creation to external calendars (all roles)
- Google Places API integration (address autocomplete)
- Postcode-first booking flow
- Staff area/postcode assignment with radius
- Coupon/discount system
- Custom fields support
- Recurring appointments
- Extras/add-ons system

## Project Structure

```
booking_system/
├── config/              # Django settings
├── apps/
│   ├── core/           # Core models, utilities
│   ├── accounts/       # User authentication
│   ├── services/       # Service & category management
│   ├── staff/          # Staff member management
│   ├── customers/      # Customer management
│   ├── appointments/   # Appointment booking & scheduling
│   ├── payments/       # Payment processing
│   ├── coupons/        # Discount coupons
│   ├── notifications/  # Email/SMS notifications
│   ├── calendar_sync/  # Multi-calendar sync (Google, Outlook, Apple)
│   ├── integrations/   # Third-party integrations
│   ├── admin_panel/    # Admin dashboard
│   └── api/            # REST API endpoints
├── static/             # CSS, JS, images
├── templates/          # HTML templates
├── media/              # User uploads
└── requirements.txt
```

## Setup Instructions

### 1. Prerequisites

- Python 3.10 or higher
- Node.js 18+ and npm
- SQLite (for development - included with Python)
- Redis (optional for development, required for production)

### 2. Installation

```bash
# Clone or navigate to the project directory
cd booking_system

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root (copy from `.env.example`):

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for development)
DATABASE_URL=sqlite:///db.sqlite3

# Redis (Optional for development)
REDIS_URL=redis://localhost:6379/0

# Add other API keys as needed
```

### 4. Database Setup

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 5. Create Sample Data (Optional)

```bash
# Create sample services, staff, customers, and appointments
python manage.py create_sample_data
```

This will create:
- 3 Categories (Cleaning Services, Maintenance Services, Green Spaces)
- 7 Services (based on VALclean website)
- 3 Staff members with schedules
- 3 Test users/customers
- 5 Sample appointments

### 6. Run Development Server

```bash
python manage.py runserver
```

The Django backend will be available at `http://localhost:8000`

### 7. Start Frontend (Next.js)

```bash
# Navigate to frontend directory (if separate)
cd frontend  # or wherever your Next.js app is

# Install dependencies
npm install

# Start development server
npm run dev
```

The Next.js frontend will be available at `http://localhost:3000`

### 8. Access the Application

**Frontend (Next.js):**
- **Home**: http://localhost:3000/
- **Book Appointment**: http://localhost:3000/booking/
- **Login**: http://localhost:3000/login/
- **Customer Dashboard**: http://localhost:3000/customer/dashboard/
- **Staff Dashboard**: http://localhost:3000/staff/dashboard/
- **Manager Dashboard**: http://localhost:3000/manager/dashboard/
- **Admin Dashboard**: http://localhost:3000/admin/dashboard/

**Backend (Django):**
- **API**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/
- **API Docs**: http://localhost:8000/api/docs/

## Documentation

### 🎯 Best Professional Solution (NEW - Start Here!)
- **`VALCLEAN_BEST_SOLUTION.md`** ⭐ - **Complete professional solution** combining best features from HouseCallPro and Bookly, tailored for VALClean
- **`IMPLEMENTATION_ROADMAP.md`** - **Step-by-step implementation guide** with detailed tasks, acceptance criteria, and deliverables for each phase
- **`FEATURE_COMPARISON.md`** - **Feature comparison** between HouseCallPro, Bookly, and our VALClean solution
- **`TECHNICAL_ARCHITECTURE.md`** - **Detailed technical architecture** covering system design, data flow, scalability, and deployment
- **`SOLUTION_OVERVIEW.md`** - Quick start guide and overview

### Main Documentation
- `BOOKING_SYSTEM_PLAN.md` - Complete development plan and feature specifications
- `PHASE1_COMPLETE.md` - Phase 1 implementation details
- `PHASE2_COMPLETE.md` - Phase 2 implementation details
- `PROJECT_STATUS.md` - Current project status and progress

### Implementation Details
- `HTTPS_ENFORCEMENT.md` - HTTPS enforcement documentation
- `SAMPLE_DATA_CREATED.md` - Sample data creation guide
- `BOOKING_FIX.md` - Booking system fixes
- `BOOKING_PAGES_FIX.md` - Booking pages fixes
- `DASHBOARD_FIXES.md` - Dashboard fixes
- `AUTHENTICATION_FIXES.md` - Authentication flow fixes
- `PROFILE_EDIT_FIXES.md` - Profile editing fixes
- `ROLE_BASED_DASHBOARDS.md` - Dashboard implementation

## License

[Add your license here]

