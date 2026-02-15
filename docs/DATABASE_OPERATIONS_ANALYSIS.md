# Database Operations Analysis - VALClean Application

This document provides a comprehensive overview of all processes in the VALClean application that save data and interact with the database.

## Table of Contents
1. [Database Models Overview](#database-models-overview)
2. [Create Operations](#create-operations)
3. [Update Operations](#update-operations)
4. [Delete Operations](#delete-operations)
5. [Auto-Save Triggers (Signals)](#auto-save-triggers-signals)
6. [Data Flow By Feature](#data-flow-by-feature)

---

## Database Models Overview

### Core Models

#### 1. **User & Authentication** (`apps/accounts/`)
- **User** - Custom user model with roles (admin, manager, staff, customer)
- **Profile** - User profiles with calendar sync settings
- **Manager** - Manager-specific permissions and relationships
- **Invitation** - Staff/manager/admin invitation system

#### 2. **Customers** (`apps/customers/`)
- **Customer** - Customer information (can be linked to User or guest)
- **Address** - Multiple addresses per customer (billing, service, other)

#### 3. **Staff** (`apps/staff/`)
- **Staff** - Staff member information
- **StaffSchedule** - Weekly working hours per staff
- **StaffService** - Staff-service assignments with custom pricing
- **StaffArea** - Geographic service areas (postcode + radius)

#### 4. **Services** (`apps/services/`)
- **Category** - Service categories (e.g., Cleaning, Maintenance)
- **Service** - Available services with pricing, duration, extras

#### 5. **Appointments** (`apps/appointments/`)
- **Appointment** - Service appointments (single, subscription, order-item)
- **CustomerAppointment** - Links customer to appointment with booking details

#### 6. **Orders** (`apps/orders/`)
- **Order** - Multi-service orders (supports guest checkout)
- **OrderItem** - Individual services within an order
- **ChangeRequest** - Customer requests to change order date/time

#### 7. **Subscriptions** (`apps/subscriptions/`)
- **Subscription** - Recurring service subscriptions
- **SubscriptionAppointment** - Links subscription to appointments
- **SubscriptionAppointmentChangeRequest** - Reschedule requests

#### 8. **Coupons** (`apps/coupons/`)
- **Coupon** - Discount coupons with validation rules
- **CouponUsage** - Tracks coupon usage per customer/order

#### 9. **Payments** (`apps/payments/`)
- **Payment** - (Placeholder - to be implemented)
- **Invoice** - (Placeholder - to be implemented)

#### 10. **Notifications** (`apps/notifications/`)
- (Placeholder - to be implemented)

#### 11. **Calendar Sync** (`apps/calendar_sync/`)
- (Placeholder - to be implemented)

---

## Create Operations

### 1. User Registration & Authentication

#### **Customer Registration** (`accounts/views.py` - `RegisterView`)
**Endpoint:** `POST /api/auth/register/`
- **Creates:**
  - `User` (role=customer, email verification pending)
  - `Profile` (auto-created via signals)
  - `Customer` (linked to user)
- **Workflow:**
  1. Validate email uniqueness
  2. Create User with hashed password
  3. Create Profile (defaults to Europe/London timezone)
  4. Create Customer record
  5. Send verification email (notifications)

#### **Staff/Manager/Admin Registration** (`accounts/views.py` - `RegisterView`)
**Endpoint:** `POST /api/auth/register/`
- **Creates:**
  - `User` (role=staff/manager/admin)
  - `Profile`
  - `Staff` or `Manager` (depending on role)
- **Requires:** Valid invitation token
- **Workflow:**
  1. Validate invitation token
  2. Check token not expired/used
  3. Create User with specified role
  4. Create Profile
  5. Create Staff or Manager record
  6. Mark invitation as used (`invitation.used_at = now()`)

#### **Send Invitation** (`accounts/views.py` - `InvitationViewSet`)
**Endpoint:** `POST /api/admin/invitations/`
- **Creates:**
  - `Invitation` (with unique token, 7-day expiry)
- **Permissions:** Admin only
- **Auto-generates:**
  - `token` (32-byte URL-safe token)
  - `expires_at` (now + 7 days)

---

### 2. Service Management

#### **Create Category** (`services/views.py` - `CategoryViewSet`)
**Endpoint:** `POST /api/admin/categories/`
- **Creates:** `Category`
- **Auto-generates:** `slug` (from name)
- **Permissions:** Admin only

#### **Create Service** (`services/views.py` - `ServiceViewSet`)
**Endpoint:** `POST /api/admin/services/`
- **Creates:** `Service`
- **Auto-generates:** `slug` (from name)
- **Permissions:** Admin or Staff (staff-created services require approval)
- **Special Logic:**
  - If created by staff: `approval_status = 'pending_approval'`
  - If created by admin: `approval_status = 'approved'`

---

### 3. Staff Management

#### **Create Staff** (`staff/views.py` - `StaffViewSet`)
**Endpoint:** `POST /api/admin/staff/`
- **Creates:** `Staff`
- **Optional:** Link to existing User account
- **Permissions:** Admin or Manager

#### **Create Staff Schedule** (`staff/views.py` - `StaffScheduleViewSet`)
**Endpoint:** `POST /api/admin/staff-schedules/`
- **Creates:** `StaffSchedule` (working hours per day)
- **Validation:** Unique per staff + day_of_week
- **Permissions:** Admin or Manager

#### **Assign Service to Staff** (`staff/views.py` - `StaffServiceViewSet`)
**Endpoint:** `POST /api/admin/staff-services/`
- **Creates:** `StaffService` (with optional price/duration overrides)
- **Permissions:** Admin or Manager

#### **Add Service Area** (`staff/views.py` - `StaffAreaViewSet`)
**Endpoint:** `POST /api/admin/staff-areas/`
- **Creates:** `StaffArea` (postcode + radius in miles)
- **Permissions:** Admin or Manager

---

### 4. Customer Management

#### **Create Customer** (`customers/views.py` - `CustomerViewSet`)
**Endpoint:** `POST /api/admin/customers/`
- **Creates:** `Customer`
- **Optional:** Link to existing User
- **Permissions:** Admin or Manager
- **Auto-saves:** User role to 'customer' if linked

#### **Add Customer Address** (`customers/views.py` - `AddressViewSet`)
**Endpoint:** `POST /api/admin/addresses/`
- **Creates:** `Address`
- **Supports:** Multiple addresses per customer (billing, service, other)
- **Permissions:** Admin, Manager, or Customer (own addresses)

---

### 5. Orders & Bookings

#### **Create Order (Guest or Customer)** (`orders/views.py` - `OrderPublicViewSet`)
**Endpoint:** `POST /api/orders/`
- **Creates:**
  - `Order` (with unique order_number, tracking_token)
  - `OrderItem` (for each service in cart)
- **Permissions:** Public (no auth required)
- **Auto-generates:**
  - `order_number` (ORD-YYYYMMDD-XXXXXX)
  - `tracking_token` (unique URL-safe token)
- **Guest Support:**
  - If no customer: stores `guest_email`, `guest_name`, `guest_phone`
  - Sets `is_guest_order = True`
- **Workflow:**
  1. Validate services exist and are active
  2. Calculate total price (including extras, coupons)
  3. Create Order record
  4. Create OrderItem for each service
  5. Send order confirmation email
  6. **DOES NOT create appointments yet** (created when admin confirms)

#### **Confirm Order** (`orders/views.py` - `OrderViewSet` + `orders/signals.py`)
**Endpoint:** `PATCH /api/admin/orders/{id}/` (status='confirmed')
- **Creates:**
  - `Appointment` (for each OrderItem)
  - `CustomerAppointment` (if customer exists)
- **Updates:**
  - `Order.status = 'confirmed'`
  - `OrderItem.appointment = <appointment_id>`
- **Triggers:**
  - Calendar sync (Google/Outlook/Apple)
  - Confirmation email
- **Workflow (via signal `pre_save`):**
  1. Detect status change to 'confirmed'
  2. For each OrderItem:
     - Create Appointment (status='pending')
     - Link Appointment to OrderItem
     - Create CustomerAppointment (if customer exists)
     - Calculate cancellation deadline (24h policy)
  3. Sync appointments to calendars (customer, staff, manager)
  4. Send confirmation email

---

### 6. Subscriptions

#### **Create Subscription** (`subscriptions/views.py` - `SubscriptionPublicViewSet`)
**Endpoint:** `POST /api/subscriptions/`
- **Creates:**
  - `Subscription` (with unique subscription_number, tracking_token)
- **Auto-generates:**
  - `subscription_number` (SUB-YYYYMMDD-XXXXXX)
  - `tracking_token`
  - `end_date` (calculated from start_date + duration_months)
  - `total_appointments` (calculated from frequency + duration)
- **Permissions:** Public or Customer
- **Guest Support:** Same as orders

#### **Generate Subscription Appointments** (Manual or Cron)
**Endpoint:** `POST /api/admin/subscriptions/{id}/generate-appointments/`
- **Creates:**
  - `Appointment` (for each scheduled visit)
  - `SubscriptionAppointment` (links subscription to appointment)
- **Workflow:**
  1. Calculate appointment dates based on frequency (weekly/biweekly/monthly)
  2. Create Appointment for each date
  3. Create SubscriptionAppointment with sequence_number
  4. Update Subscription.next_appointment_date

---

### 7. Appointments

#### **Book Appointment (Direct)** (`appointments/views.py` - `AppointmentPublicViewSet`)
**Endpoint:** `POST /api/appointments/`
- **Creates:**
  - `Appointment` (type='single')
  - `CustomerAppointment` (with booking details)
- **Permissions:** Public or Customer
- **Workflow:**
  1. Validate staff availability
  2. Check postcode coverage
  3. Calculate total price (service + extras)
  4. Create Appointment (status='pending')
  5. Create CustomerAppointment
  6. Calculate cancellation deadline (24h policy)
  7. Send booking confirmation email

#### **Reschedule Appointment** (`appointments/views.py`)
**Endpoint:** `PATCH /api/appointments/{id}/reschedule/`
- **Updates:**
  - `Appointment.start_time`
  - `Appointment.end_time`
  - `CustomerAppointment.cancellation_deadline`
- **Triggers:**
  - Calendar event update
  - Notification email

#### **Cancel Appointment** (`appointments/views.py`)
**Endpoint:** `PATCH /api/appointments/{id}/cancel/`
- **Updates:**
  - `Appointment.status = 'cancelled'`
- **Validation:** Check `can_cancel` (24h policy)
- **Triggers:**
  - Calendar event deletion
  - Cancellation email

---

### 8. Coupons

#### **Create Coupon** (`coupons/views.py` - `CouponViewSet`)
**Endpoint:** `POST /api/admin/coupons/`
- **Creates:** `Coupon`
- **Permissions:** Admin only
- **Validation:**
  - Unique code
  - Percentage discount ≤ 100%
- **Auto-updates:** `status = 'expired'` if past valid_until

#### **Apply Coupon to Order** (During order creation)
**Endpoint:** `POST /api/orders/` (with coupon_code)
- **Creates:** `CouponUsage`
- **Updates:**
  - `Coupon.used_count += 1`
  - `Order.total_price` (after discount)
- **Validation:**
  - Coupon is active
  - Not expired
  - Max uses not reached
  - Per-customer limit not exceeded
  - Minimum order amount met
  - Service restrictions met

---

### 9. Change Requests

#### **Request Order Date Change** (`orders/views.py` - `ChangeRequestViewSet`)
**Endpoint:** `POST /api/orders/{id}/change-requests/`
- **Creates:** `ChangeRequest` (status='pending')
- **Permissions:** Customer or Guest (via tracking_token)
- **Workflow:**
  1. Create ChangeRequest
  2. Notify admin/manager
  3. Admin reviews and approves/rejects

#### **Approve Change Request** (`orders/views.py`)
**Endpoint:** `PATCH /api/admin/change-requests/{id}/` (status='approved')
- **Updates:**
  - `ChangeRequest.status = 'approved'`
  - `Order.scheduled_date` (to requested_date)
  - `Order.scheduled_time` (to requested_time)
  - All related `Appointment.start_time` and `end_time`
- **Triggers:**
  - Calendar event updates
  - Notification to customer

---

### 10. Calendar Sync

#### **Connect Google Calendar** (`calendar_sync/views.py` - `GoogleCalendarConnectView`)
**Endpoint:** `POST /api/calendar/google/connect/`
- **Updates:**
  - `Profile.calendar_sync_enabled = True`
  - `Profile.calendar_provider = 'google'`
  - `Profile.calendar_access_token` (encrypted)
  - `Profile.calendar_refresh_token` (encrypted)
  - `Profile.calendar_calendar_id`
- **Permissions:** Authenticated user

#### **Sync Appointment to Calendar** (Auto-triggered)
**Trigger:** Order confirmation, appointment creation
- **Updates:**
  - `Appointment.calendar_event_id` (JSON: {google: "event_id", ...})
  - `Appointment.calendar_synced_to` (JSON array: ["google", "outlook"])
- **Syncs to:**
  - Customer calendar (if enabled)
  - Staff calendar (if enabled)
  - Manager calendar (if enabled)

#### **Manual Sync All Appointments** (`calendar_sync/views.py` - `ManualSyncView`)
**Endpoint:** `POST /api/calendar/manual-sync/`
- **Updates:** All user's appointments to calendar
- **Permissions:** Authenticated user

---

## Update Operations

### 1. User & Profile Updates

#### **Update Profile** (`accounts/views.py` - `ProfileViewSet`)
**Endpoint:** `PATCH /api/profile/`
- **Updates:** `Profile` (phone, avatar, timezone, preferences)
- **Permissions:** Owner only

#### **Update User Role** (`accounts/views.py` - `UserViewSet`)
**Endpoint:** `PATCH /api/admin/users/{id}/`
- **Updates:** `User.role`
- **Permissions:** Admin only
- **Side Effects:**
  - Creates Staff/Manager/Customer record if role changes

---

### 2. Service Updates

#### **Update Service** (`services/views.py` - `ServiceViewSet`)
**Endpoint:** `PATCH /api/admin/services/{id}/`
- **Updates:** `Service` (price, duration, extras, etc.)
- **Permissions:** Admin only
- **Special Logic:**
  - Admin can approve staff-created services: `approval_status = 'approved'`

#### **Deactivate Service** (`services/views.py`)
**Endpoint:** `PATCH /api/admin/services/{id}/` (is_active=False)
- **Updates:** `Service.is_active = False`
- **Side Effects:**
  - Service no longer bookable
  - Existing appointments unaffected

---

### 3. Staff Updates

#### **Update Staff Details** (`staff/views.py` - `StaffViewSet`)
**Endpoint:** `PATCH /api/admin/staff/{id}/`
- **Updates:** `Staff` (name, email, phone, bio, photo)
- **Permissions:** Admin or Manager

#### **Update Staff Schedule** (`staff/views.py` - `StaffScheduleViewSet`)
**Endpoint:** `PATCH /api/admin/staff-schedules/{id}/`
- **Updates:** `StaffSchedule` (start_time, end_time, breaks)
- **Permissions:** Admin or Manager

#### **Update Staff Service Pricing** (`staff/views.py` - `StaffServiceViewSet`)
**Endpoint:** `PATCH /api/admin/staff-services/{id}/`
- **Updates:** `StaffService` (price_override, duration_override)
- **Permissions:** Admin or Manager

---

### 4. Order Updates

#### **Update Order Status** (`orders/views.py` - `OrderViewSet`)
**Endpoint:** `PATCH /api/admin/orders/{id}/`
- **Updates:** `Order.status`
- **Permissions:** Admin or Manager
- **Triggers (via signal):**
  - If status → 'confirmed': Create appointments + sync calendars
  - If status → 'completed': Update payment status
  - If status → 'cancelled': Cancel all appointments

#### **Assign Staff to Order Item** (`orders/views.py`)
**Endpoint:** `PATCH /api/admin/order-items/{id}/`
- **Updates:** `OrderItem.staff`
- **Permissions:** Admin or Manager

#### **Link Guest Order to Customer** (After customer registers)
**Endpoint:** `POST /api/orders/{tracking_token}/link-account/`
- **Updates:**
  - `Order.customer = <customer_id>`
  - `Order.account_linked_at = now()`
- **Side Effects:**
  - Guest order now visible in customer dashboard

---

### 5. Appointment Updates

#### **Update Appointment Status** (`appointments/views.py` - `AppointmentViewSet`)
**Endpoint:** `PATCH /api/admin/appointments/{id}/`
- **Updates:** `Appointment.status`
- **Permissions:** Admin, Manager, or Staff (own appointments)
- **Triggers:**
  - Calendar event update
  - Notification to customer

#### **Upload Completion Photos** (`appointments/views.py`)
**Endpoint:** `POST /api/appointments/{id}/upload-photos/`
- **Updates:** `Appointment.completion_photos` (JSON array of URLs)
- **Permissions:** Staff (assigned to appointment)

#### **Add Internal Notes** (`appointments/views.py`)
**Endpoint:** `PATCH /api/admin/appointments/{id}/`
- **Updates:** `Appointment.internal_notes`
- **Permissions:** Admin, Manager, or Staff

---

### 6. Subscription Updates

#### **Pause Subscription** (`subscriptions/views.py`)
**Endpoint:** `PATCH /api/subscriptions/{id}/pause/`
- **Updates:** `Subscription.status = 'paused'`
- **Side Effects:**
  - Future appointments cancelled
  - `next_appointment_date = null`

#### **Resume Subscription** (`subscriptions/views.py`)
**Endpoint:** `PATCH /api/subscriptions/{id}/resume/`
- **Updates:** `Subscription.status = 'active'`
- **Side Effects:**
  - Recalculate next_appointment_date
  - Generate new appointments

#### **Complete Subscription Appointment** (`subscriptions/views.py`)
**Endpoint:** `PATCH /api/subscriptions/{id}/appointments/{seq}/complete/`
- **Updates:**
  - `SubscriptionAppointment.status = 'completed'`
  - `Subscription.completed_appointments += 1`
- **Side Effects:**
  - If all appointments completed: `Subscription.status = 'completed'`

---

### 7. Manager Permissions

#### **Update Manager Permissions** (`accounts/views.py` - `ManagerViewSet`)
**Endpoint:** `PATCH /api/admin/managers/{id}/`
- **Updates:** `Manager` (permissions, can_manage_all, etc.)
- **Permissions:** Admin only
- **Allows:**
  - Assign/remove managed staff
  - Assign/remove managed customers
  - Grant/revoke permissions

---

## Delete Operations

### 1. Soft Deletes (Preferred)

Most entities use **soft deletion** (set `is_active = False` or `status = 'cancelled'`):

- **Services:** `is_active = False`
- **Staff:** `is_active = False`
- **Customers:** No deletion (archive via tags)
- **Appointments:** `status = 'cancelled'`
- **Orders:** `status = 'cancelled'`
- **Subscriptions:** `status = 'cancelled'`
- **Coupons:** `status = 'inactive'`

### 2. Hard Deletes (Cascading)

These entities can be hard-deleted:

#### **Delete Invitation** (`accounts/views.py` - `InvitationViewSet`)
**Endpoint:** `DELETE /api/admin/invitations/{id}/`
- **Deletes:** `Invitation`
- **Permissions:** Admin only
- **Safe:** Only unused/expired invitations

#### **Delete Address** (`customers/views.py` - `AddressViewSet`)
**Endpoint:** `DELETE /api/admin/addresses/{id}/`
- **Deletes:** `Address`
- **Permissions:** Admin, Manager, or Customer (own)
- **Validation:** Cannot delete if `is_default = True` (must set another default first)

#### **Delete Staff Schedule** (`staff/views.py` - `StaffScheduleViewSet`)
**Endpoint:** `DELETE /api/admin/staff-schedules/{id}/`
- **Deletes:** `StaffSchedule`
- **Permissions:** Admin or Manager

#### **Delete Staff Area** (`staff/views.py` - `StaffAreaViewSet`)
**Endpoint:** `DELETE /api/admin/staff-areas/{id}/`
- **Deletes:** `StaffArea`
- **Permissions:** Admin or Manager

#### **Delete Staff Service Assignment** (`staff/views.py` - `StaffServiceViewSet`)
**Endpoint:** `DELETE /api/admin/staff-services/{id}/`
- **Deletes:** `StaffService`
- **Permissions:** Admin or Manager
- **Side Effect:** Staff can no longer perform this service

---

## Auto-Save Triggers (Signals)

### Django Signals (`apps/orders/signals.py`)

#### **Order Confirmation Signal** (`pre_save` on Order)
**Trigger:** `Order.status` changes to 'confirmed'
- **Creates:**
  - Appointments for all OrderItems
  - CustomerAppointments
- **Updates:**
  - `OrderItem.appointment`
  - `Appointment.calendar_event_id`
- **Sends:**
  - Confirmation email
  - Calendar invites

---

## Data Flow By Feature

### Feature 1: Guest Checkout (No Login)

**Flow:**
1. Guest visits website → Browses services
2. Adds services to cart → Enters details (name, email, address)
3. Applies coupon (optional) → Submits order
4. **DATABASE SAVES:**
   - `Order` (with guest_email, guest_name, tracking_token)
   - `OrderItem` (for each service)
   - `CouponUsage` (if coupon applied)
5. System sends email with tracking link
6. Admin reviews → Assigns staff → Confirms order
7. **DATABASE SAVES (via signal):**
   - `Appointment` (for each OrderItem)
   - `CustomerAppointment` (if guest registers later)
   - `Appointment.calendar_event_id` (syncs to calendars)
8. System sends confirmation email with appointment details

**Later:** Guest registers account → System links order to customer
- **DATABASE UPDATE:** `Order.customer = <customer_id>`

---

### Feature 2: Customer Subscription

**Flow:**
1. Customer browses services → Selects subscription (weekly/monthly)
2. Chooses frequency, duration, start date → Submits
3. **DATABASE SAVES:**
   - `Subscription` (with tracking_token, guest support)
   - `Coupon.used_count++` (if coupon applied)
   - `CouponUsage`
4. Admin reviews → Confirms subscription → Generates appointments
5. **DATABASE SAVES:**
   - `Appointment` (for each scheduled visit)
   - `SubscriptionAppointment` (with sequence_number)
   - `Appointment.calendar_event_id` (syncs to calendars)
6. System sends confirmation + calendar invites

**During Subscription:**
- Customer requests reschedule of visit #3 → **CREATES:** `SubscriptionAppointmentChangeRequest`
- Admin approves → **UPDATES:** `Appointment.start_time`, updates calendar
- Staff completes visit → **UPDATES:** `SubscriptionAppointment.status = 'completed'`
- System auto-updates: `Subscription.completed_appointments++`

---

### Feature 3: Staff Self-Service

**Flow:**
1. Staff logs in → Views assigned appointments
2. Staff creates new service offering (e.g., "Premium Window Cleaning")
3. **DATABASE SAVES:**
   - `Service` (with `created_by_staff = <staff_id>`, `approval_status = 'pending_approval'`)
4. Admin reviews → Approves service
5. **DATABASE UPDATE:** `Service.approval_status = 'approved'`
6. Staff updates own schedule
7. **DATABASE UPDATES:** `StaffSchedule` (working hours)
8. Staff adds service area
9. **DATABASE CREATES:** `StaffArea` (postcode + radius)

---

### Feature 4: Manager Dashboard

**Flow:**
1. Admin creates manager account → Sends invitation
2. **DATABASE SAVES:**
   - `Invitation` (token, role=manager, expires in 7 days)
3. Manager registers via invitation link
4. **DATABASE SAVES:**
   - `User` (role=manager)
   - `Profile`
   - `Manager` (with permissions)
5. Admin assigns permissions to manager
6. **DATABASE UPDATES:**
   - `Manager.can_manage_staff = True`
   - `Manager.managed_staff.add(<staff_ids>)`
7. Manager views staff schedules → Assigns staff to orders
8. **DATABASE UPDATE:** `OrderItem.staff = <staff_id>`
9. Manager approves staff-created services
10. **DATABASE UPDATE:** `Service.approval_status = 'approved'`

---

### Feature 5: Calendar Sync

**Flow:**
1. User (any role) connects Google Calendar
2. **DATABASE SAVES:**
   - `Profile.calendar_sync_enabled = True`
   - `Profile.calendar_provider = 'google'`
   - `Profile.calendar_access_token` (encrypted)
   - `Profile.calendar_refresh_token` (encrypted)
3. System auto-syncs all user's appointments → Creates events in Google Calendar
4. **DATABASE UPDATES:**
   - `Appointment.calendar_event_id = {"google": "event_12345"}`
   - `Appointment.calendar_synced_to = ["google"]`
5. When appointment is rescheduled → System updates Google Calendar event
6. **DATABASE UPDATE:** `Appointment.start_time` → Triggers calendar update

---

### Feature 6: Coupon System

**Flow:**
1. Admin creates coupon (e.g., "SAVE20" - 20% off)
2. **DATABASE SAVES:**
   - `Coupon` (code, discount_type, discount_value, valid_from, valid_until)
3. Customer applies coupon during checkout
4. System validates coupon:
   - Check `status = 'active'`
   - Check not expired (`valid_until > now()`)
   - Check max_uses not exceeded
   - Check per-customer limit
   - Check minimum order amount
   - Check service restrictions
5. **DATABASE SAVES:**
   - `CouponUsage` (customer, order, discount_amount)
6. **DATABASE UPDATES:**
   - `Coupon.used_count++`
   - `Order.total_price` (after discount)

---

## Summary of All Database Write Operations

### **Total Models:** 25

### **Models with CREATE operations:** 20
1. User
2. Profile
3. Manager
4. Invitation
5. Customer
6. Address
7. Staff
8. StaffSchedule
9. StaffService
10. StaffArea
11. Category
12. Service
13. Appointment
14. CustomerAppointment
15. Order
16. OrderItem
17. ChangeRequest
18. Subscription
19. SubscriptionAppointment
20. SubscriptionAppointmentChangeRequest
21. Coupon
22. CouponUsage

### **Models with UPDATE operations:** 18
1. User (role changes)
2. Profile (settings, calendar tokens)
3. Manager (permissions)
4. Invitation (used_at)
5. Customer (details)
6. Staff (details, active status)
7. StaffSchedule (hours)
8. StaffService (pricing overrides)
9. Service (price, duration, approval)
10. Appointment (status, times, photos, notes)
11. CustomerAppointment (payment status)
12. Order (status, scheduled date)
13. OrderItem (staff assignment)
14. ChangeRequest (status, review)
15. Subscription (status, next date)
16. SubscriptionAppointment (status)
17. Coupon (used_count, status)
18. CouponUsage (tracking)

### **Models with DELETE operations:** 5
1. Invitation (hard delete)
2. Address (hard delete)
3. StaffSchedule (hard delete)
4. StaffArea (hard delete)
5. StaffService (hard delete)

### **Models with SOFT DELETE:** 7
1. User (is_active)
2. Staff (is_active)
3. Service (is_active)
4. Appointment (status='cancelled')
5. Order (status='cancelled')
6. Subscription (status='cancelled')
7. Coupon (status='inactive')

---

## Key Auto-Save Behaviors

### 1. **Model `save()` Overrides** (Auto-updates on save)

- **User:** Normalizes email to lowercase
- **Customer:** Sets user.role = 'customer' if user linked
- **Staff:** Sets user.role = 'staff' if user linked
- **Service:** Auto-generates slug from name
- **Category:** Auto-generates slug from name
- **Order:** Generates order_number, tracking_token, calculates cancellation deadline
- **Subscription:** Generates subscription_number, tracking_token
- **OrderItem:** Calculates total_price (quantity × unit_price)
- **Invitation:** Generates token, sets expires_at (now + 7 days)
- **Coupon:** Validates discount_value, auto-updates status if expired
- **SubscriptionAppointment:** Calculates cancellation deadline

### 2. **Django Signals** (Triggers after save)

- **Order status → 'confirmed':**
  - Creates Appointments for OrderItems
  - Creates CustomerAppointments
  - Syncs to calendars (customer, staff, manager)
  - Sends confirmation email

### 3. **Cascading Deletes** (ON_DELETE rules)

- **User → Profile:** CASCADE (delete profile if user deleted)
- **User → Manager:** CASCADE
- **Customer → Order:** SET_NULL (keep order if customer deleted)
- **Customer → Address:** CASCADE
- **Staff → StaffSchedule:** CASCADE
- **Staff → StaffService:** CASCADE
- **Staff → StaffArea:** CASCADE
- **Service → Appointment:** CASCADE
- **Order → OrderItem:** CASCADE
- **Subscription → SubscriptionAppointment:** CASCADE
- **Appointment → CustomerAppointment:** CASCADE
- **Coupon → CouponUsage:** CASCADE

---

## Recommended Next Steps

1. **Implement Payment Models:**
   - Payment (Stripe integration)
   - Invoice (PDF generation)

2. **Implement Notification Models:**
   - EmailLog (track sent emails)
   - SMSLog (track sent SMS)
   - NotificationPreference (per-user settings)

3. **Add Audit Trail:**
   - Create `AuditLog` model to track all CUD operations
   - Log user, action, model, old_value, new_value, timestamp

4. **Add Data Validation:**
   - Implement clean() methods on models
   - Add database constraints (CHECK constraints)
   - Add custom validators for business rules

5. **Optimize Database Performance:**
   - Add database indexes on frequently queried fields
   - Use select_related() and prefetch_related() in views
   - Add database-level caching (Redis)

6. **Implement Backup Strategy:**
   - Daily automated backups
   - Point-in-time recovery
   - Test restore procedures

---

**Last Updated:** 2026-02-15
**Version:** 1.0
**Maintained By:** Development Team
