# Week 1 Database Information

## Database Status Check

**Date:** January 11, 2026  
**Database:** SQLite (db.sqlite3)  
**Total Tables:** 14 tables

---

## ✅ Tables Currently in Database

### 1. **accounts_user** (1 record)
- **Purpose:** Custom User model with roles (admin, manager, staff, customer)
- **Records:** 1 user (admin superuser)
- **Key Fields:**
  - `id`, `email`, `username`, `password`
  - `role` (admin/manager/staff/customer)
  - `is_verified`, `is_superuser`, `is_staff`, `is_active`
  - `first_name`, `last_name`, `date_joined`, `last_login`

**Current Data:**
- 1 admin user created (email: admin@valclean.uk, username: admin)

### 2. **accounts_profile** (0 records)
- **Purpose:** User profiles with calendar sync capabilities
- **Records:** 0 (no profiles created yet)
- **Key Fields:**
  - `user` (OneToOne to User)
  - `phone`, `avatar`, `timezone`, `preferences`
  - `calendar_sync_enabled`, `calendar_provider` (google/outlook/apple/none)
  - `calendar_access_token`, `calendar_refresh_token`, `calendar_calendar_id`
  - `calendar_sync_settings` (JSON)

### 3. **accounts_manager** (0 records)
- **Purpose:** Manager model with flexible permissions
- **Records:** 0 (no managers created yet)
- **Key Fields:**
  - `user` (OneToOne to User with role=manager)
  - `permissions` (JSON), `can_manage_all`, `can_manage_customers`
  - `can_manage_staff`, `can_manage_appointments`, `can_view_reports`
  - `managed_locations` (JSON), `is_active`
  - ManyToMany: `managed_staff`, `managed_customers`

### 4. **accounts_manager_managed_customers** (0 records)
- **Purpose:** ManyToMany relationship table (Manager ↔ Customer)
- **Records:** 0

### 5. **accounts_manager_managed_staff** (0 records)
- **Purpose:** ManyToMany relationship table (Manager ↔ Staff)
- **Records:** 0

### 6. **accounts_user_groups** (0 records)
- **Purpose:** Django groups for users
- **Records:** 0

### 7. **accounts_user_user_permissions** (0 records)
- **Purpose:** Django permissions for users
- **Records:** 0

### 8. **django_session** (1 record)
- **Purpose:** Django session storage
- **Records:** 1 active session

### 9. **django_migrations** (19 records)
- **Purpose:** Django migration tracking
- **Records:** 19 migrations applied
- **Applied Apps:**
  - contenttypes
  - auth
  - admin
  - sessions
  - accounts (only accounts app has migrations)

### 10. **django_content_type** (22 records)
- **Purpose:** Django content types
- **Records:** 22 content types registered

### 11. **auth_permission** (88 records)
- **Purpose:** Django permissions
- **Records:** 88 permissions

### 12. **auth_group** (0 records)
- **Purpose:** Django groups
- **Records:** 0

### 13. **auth_group_permissions** (0 records)
- **Purpose:** Group permissions
- **Records:** 0

### 14. **django_admin_log** (0 records)
- **Purpose:** Django admin action log
- **Records:** 0

---

## ❌ Tables NOT Yet Created (Migrations Not Applied)

The following models were created in Week 1 but migrations haven't been run yet:

### Services App
- ❌ **services_category** - Service categories (e.g., Cleaning, Maintenance, Green Spaces)
- ❌ **services_service** - Services (e.g., Window Cleaning, Grass Cutting)

### Staff App
- ❌ **staff_staff** - Staff members
- ❌ **staff_staffschedule** - Staff working hours
- ❌ **staff_staffarea** - Staff service areas (postcode + radius)
- ❌ **staff_staffservice** - Staff-Service relationships with price/duration overrides

### Customers App
- ❌ **customers_customer** - Customers (can be linked to User or standalone for guests)
- ❌ **customers_address** - Customer addresses (multiple addresses per customer)

### Appointments App
- ❌ **appointments_appointment** - Appointments with calendar sync support
- ❌ **appointments_customerappointment** - Customer booking details with payment and cancellation policy

### Orders App
- ❌ **orders_order** - Orders with guest checkout support (multi-service orders)
- ❌ **orders_orderitem** - Order items (services in an order)

### Subscriptions App
- ❌ **subscriptions_subscription** - Subscriptions with guest checkout (recurring services)
- ❌ **subscriptions_subscriptionappointment** - Subscription appointment instances

---

## 📊 Summary

### What's Currently Saved:
1. **1 Admin User** - Created during superuser setup
2. **User Model Structure** - Custom user with roles
3. **Profile Model Structure** - Ready for calendar sync
4. **Manager Model Structure** - Ready for permission management
5. **Django System Tables** - Sessions, permissions, content types

### What Needs to Be Created:
- **All other app models** - Need to run migrations:
  ```bash
  cd backend
  .\venv\Scripts\python.exe manage.py makemigrations
  .\venv\Scripts\python.exe manage.py migrate
  ```

---

## 🔍 Week 1 Models Created (Code Level)

Even though migrations haven't been run, the following models were **created in code** during Week 1:

### Accounts App ✅
- ✅ User (Custom user with roles)
- ✅ Profile (Calendar sync fields)
- ✅ Manager (Permission system)

### Services App 📝
- 📝 Category (Service categories)
- 📝 Service (Services with pricing, duration, capacity)

### Staff App 📝
- 📝 Staff (Staff members)
- 📝 StaffSchedule (Working hours)
- 📝 StaffArea (Service areas with postcode + radius)
- 📝 StaffService (Staff-Service relationships)

### Customers App 📝
- 📝 Customer (Customers with guest support)
- 📝 Address (Multiple addresses per customer)

### Appointments App 📝
- 📝 Appointment (Appointments with calendar sync)
- 📝 CustomerAppointment (Booking details with cancellation policy)

### Orders App 📝
- 📝 Order (Multi-service orders with guest checkout)
- 📝 OrderItem (Order items)

### Subscriptions App 📝
- 📝 Subscription (Recurring services with guest checkout)
- 📝 SubscriptionAppointment (Subscription instances)

---

## 📝 Next Steps

To complete Week 1 database setup:

1. **Create migrations for all apps:**
   ```bash
   cd backend
   .\venv\Scripts\python.exe manage.py makemigrations
   ```

2. **Apply migrations:**
   ```bash
   .\venv\Scripts\python.exe manage.py migrate
   ```

3. **Verify all tables are created:**
   ```bash
   .\venv\Scripts\python.exe check_db_info.py
   ```

---

## 📋 Database Schema Information

All models include:
- `created_at` - Timestamp when record was created
- `updated_at` - Timestamp when record was last updated
- Proper indexes for performance
- Foreign key relationships
- JSON fields for flexible data storage (calendar sync, preferences, etc.)

---

**Note:** This document reflects the current state of the database. After running migrations, all Week 1 models will be available in the database.
