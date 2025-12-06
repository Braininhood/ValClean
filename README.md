# Booking System - Django Project

A comprehensive appointment booking system built with Django, inspired by professional booking platforms.

## Features

### ✅ Implemented (Phase 1 & 2)
- ✅ Multi-step booking workflow (8 steps)
- ✅ Staff and service management (full CRUD)
- ✅ Customer management with address fields
- ✅ Appointment scheduling with time slot calculation
- ✅ Role-based authentication (Admin, Staff, Customer)
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
- Calendar integration (Google, Outlook, Apple)
- Royal Mail AddressNow integration
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
- PostgreSQL (for production) or SQLite (for development)
- Redis (for caching and Celery)

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

# Redis
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

The application will be available at `http://localhost:8000`

### 7. Access the Application

- **Home**: http://localhost:8000/
- **Book Appointment**: http://localhost:8000/appointments/booking/
- **Login**: http://localhost:8000/accounts/login/
- **Register**: http://localhost:8000/accounts/register/
- **Admin**: http://localhost:8000/admin/
- **Customer Dashboard**: http://localhost:8000/customers/dashboard/ (after login as customer)
- **Staff Dashboard**: http://localhost:8000/staff/dashboard/ (after login as staff)

## Apps Overview

### Core
Base models and utilities used across the project.

### Services
- Category management
- Service management (simple and compound services)
- Service pricing and capacity

### Staff
- Staff member profiles
- Weekly schedules with breaks
- Holiday management
- Staff-service associations with custom pricing
- Calendar integration per staff

### Customers
- Customer profiles
- Address management with Royal Mail AddressNow integration
- Customer history

### Appointments
- Appointment scheduling
- Customer-appointment relationships
- Recurring appointments (series)
- Status management (pending, approved, cancelled, rejected)

### Payments
- Multiple payment gateway support
- Payment tracking and status
- Refund management

### Coupons
- Discount codes
- Percentage and fixed amount discounts
- Usage limits and service restrictions

### Notifications
- Email and SMS templates
- Notification sending and tracking
- Reminder system

### Calendar Sync
- Google Calendar integration
- Microsoft Outlook integration
- Apple Calendar support
- Two-way sync capabilities

### Integrations
- Custom fields for booking forms
- Third-party service integrations

## Development

### Running Tests

```bash
pytest
```

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Collecting Static Files

```bash
python manage.py collectstatic
```

## API Documentation

API documentation will be available at `/api/docs/` once Swagger/OpenAPI is configured.

## Current Status

### ✅ Phase 1: Core Foundation - COMPLETE
- User authentication with role-based access
- Services, Staff, and Customers CRUD operations
- Role-based dashboards
- HTTPS enforcement
- Profile editing

### ✅ Phase 2: Booking Engine - COMPLETE
- Multi-step booking workflow (8 steps)
- Time slot calculation
- Session management
- Appointment creation
- All booking templates created

### ✅ Phase 3: Payment Integration - COMPLETE
- Payment gateway integration (Stripe, PayPal)
- Payment processing workflow
- Payment templates and views

### ✅ Phase 4: Notifications - COMPLETE
- Email notification system
- SMS notification system (Twilio)
- Automatic notification triggers
- Reminder system (Celery)
- Template management

### 🚧 Phase 5: Advanced Features - PLANNED
- Calendar sync (Google, Outlook, Apple)
- Royal Mail AddressNow integration
- Coupon system integration
- Custom fields
- Recurring appointments

## Next Steps

1. **Configure Notifications** (See `NOTIFICATION_CONFIGURATION_GUIDE.md`):
   - Set up email service (SendGrid/Gmail)
   - Configure SMS service (Twilio)
   - Set up Celery for reminders

2. **Configure Payment Gateways** (See `PHASE3_PAYMENT_INTEGRATION.md`):
   - Add Stripe API keys
   - Add PayPal API keys

3. **Phase 5: Advanced Features**:
   - Calendar sync (Google, Outlook, Apple)
   - Royal Mail AddressNow integration
   - Coupon system
   - Custom fields
   - Recurring appointments

## Documentation

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

