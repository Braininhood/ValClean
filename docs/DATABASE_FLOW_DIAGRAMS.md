# Database Flow Diagrams - VALClean Application

This document provides visual representations of data flows for key features in the VALClean application.

## Table of Contents
1. [Guest Order Flow](#guest-order-flow)
2. [Subscription Flow](#subscription-flow)
3. [Appointment Creation Flow](#appointment-creation-flow)
4. [User Registration Flow](#user-registration-flow)
5. [Calendar Sync Flow](#calendar-sync-flow)
6. [Coupon Application Flow](#coupon-application-flow)
7. [Order Confirmation Flow](#order-confirmation-flow)

---

## Guest Order Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ GUEST CHECKOUT (No Login Required)                                  │
└─────────────────────────────────────────────────────────────────────┘

[Customer Action]           [Database Operations]              [Side Effects]

1. Browse Services
   └─► READ: Service (is_active=True)
   └─► READ: Category

2. Add to Cart
   └─► (Client-side only)

3. Enter Details
   │  - Name
   │  - Email
   │  - Phone
   │  - Address
   │  - Postcode
   └─► VALIDATE: Postcode (Google Places API)

4. Apply Coupon (optional)
   └─► READ: Coupon (code)
   └─► VALIDATE: is_valid(service_ids, order_amount)
       - Check expiry
       - Check max_uses
       - Check service restrictions

5. Submit Order
   ├─► CREATE: Order
   │   │  - order_number: "ORD-20260215-ABC123"
   │   │  - tracking_token: "xyz789..."
   │   │  - guest_email: "customer@example.com"
   │   │  - guest_name: "John Doe"
   │   │  - is_guest_order: True
   │   │  - status: "pending"
   │   │  - total_price: £150.00
   │   │  - address fields
   │   └─► Auto-generates: order_number, tracking_token
   │
   ├─► CREATE: OrderItem (for each service)
   │   │  - order: <order_id>
   │   │  - service: <service_id>
   │   │  - quantity: 1
   │   │  - unit_price: £75.00
   │   │  - total_price: £75.00 (auto-calculated)
   │   └─► Auto-calculates: total_price = quantity × unit_price
   │
   └─► IF coupon applied:
       ├─► CREATE: CouponUsage
       │   │  - coupon: <coupon_id>
       │   │  - guest_email: "customer@example.com"
       │   │  - order: <order_id>
       │   │  - discount_amount: £30.00
       │   │  - order_amount: £150.00
       │   └─► final_amount: £120.00
       │
       └─► UPDATE: Coupon.used_count++

6. System Response
   ├─► Send email confirmation
   │   - Order details
   │   - Tracking link: /orders/track/{tracking_token}
   │
   └─► Return: Order details + tracking_token

7. Admin Reviews Order
   ├─► READ: Order (status='pending')
   └─► ASSIGN Staff to OrderItems

8. Admin Confirms Order
   └─► UPDATE: Order.status = 'confirmed'
       └─► TRIGGER: Order Confirmation Flow (see below)

═══════════════════════════════════════════════════════════════════════

LATER: Guest Registers Account

9. Guest registers with same email
   ├─► CREATE: User (email, role='customer')
   ├─► CREATE: Profile
   └─► CREATE: Customer (user, name, email)

10. System Links Order
    └─► UPDATE: Order
        │  - customer: <customer_id>
        └─► account_linked_at: now()
```

---

## Subscription Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ SUBSCRIPTION CREATION & MANAGEMENT                                   │
└─────────────────────────────────────────────────────────────────────┘

[Customer Action]           [Database Operations]              [Calculations]

1. Select Service
   └─► READ: Service (is_active=True, approval_status='approved')

2. Choose Subscription Options
   │  - Frequency: weekly/biweekly/monthly
   │  - Duration: 1, 2, 3, 6, or 12 months
   └─► Start Date

3. Calculate Total
   │  - Weekly: ~4 visits/month
   │  - Biweekly: ~2 visits/month
   │  - Monthly: 1 visit/month
   │
   Example: 3 months, weekly, £50/visit
   └─► Total appointments: 12
       Total price: £600

4. Submit Subscription
   ├─► CREATE: Subscription
   │   │  - subscription_number: "SUB-20260215-XYZ456"
   │   │  - tracking_token: "abc123..."
   │   │  - guest_email OR customer_id
   │   │  - service: <service_id>
   │   │  - staff: <staff_id> (optional)
   │   │  - frequency: "weekly"
   │   │  - duration_months: 3
   │   │  - start_date: 2026-02-20
   │   │  - end_date: 2026-05-20 (calculated)
   │   │  - total_appointments: 12 (calculated)
   │   │  - price_per_appointment: £50.00
   │   │  - total_price: £600.00
   │   │  - status: "active"
   │   │  - next_appointment_date: 2026-02-20
   │   └─► Auto-generates: subscription_number, tracking_token, end_date
   │
   └─► IF coupon applied:
       ├─► CREATE: CouponUsage
       └─► UPDATE: Coupon.used_count++

5. Admin Confirms Subscription
   └─► Generate Appointments

6. Generate Appointments (Manual or Cron)
   │
   For each scheduled visit (12 visits):
   │
   ├─► CREATE: Appointment
   │   │  - staff: <staff_id>
   │   │  - service: <service_id>
   │   │  - start_time: 2026-02-20 09:00:00 (visit 1)
   │   │  - end_time: 2026-02-20 11:00:00 (duration 120 mins)
   │   │  - status: "pending"
   │   │  - appointment_type: "subscription"
   │   └─► subscription: <subscription_id>
   │
   └─► CREATE: SubscriptionAppointment
       │  - subscription: <subscription_id>
       │  - appointment: <appointment_id>
       │  - sequence_number: 1, 2, 3... 12
       │  - scheduled_date: 2026-02-20, 2026-02-27...
       │  - status: "scheduled"
       │  - can_cancel: True
       │  - can_reschedule: True
       └─► cancellation_deadline: 2026-02-19 09:00:00 (24h before)

7. Sync to Calendars
   └─► For each appointment:
       └─► UPDATE: Appointment
           │  - calendar_event_id: {"google": "event_123"}
           └─► calendar_synced_to: ["google"]

═══════════════════════════════════════════════════════════════════════

DURING SUBSCRIPTION: Customer Reschedules Visit

8. Customer Requests Reschedule (Visit #3)
   ├─► CREATE: SubscriptionAppointmentChangeRequest
   │   │  - subscription_appointment: <sub_appt_id>
   │   │  - requested_date: 2026-03-10
   │   │  - requested_time: 14:00:00
   │   │  - reason: "I'll be away"
   │   └─► status: "pending"
   │
   └─► Notify admin/manager

9. Admin Approves Request
   ├─► UPDATE: SubscriptionAppointmentChangeRequest
   │   │  - status: "approved"
   │   │  - reviewed_by: <admin_user_id>
   │   └─► reviewed_at: now()
   │
   └─► UPDATE: Appointment
       │  - start_time: 2026-03-10 14:00:00
       │  - end_time: 2026-03-10 16:00:00
       └─► Trigger: Calendar event update

═══════════════════════════════════════════════════════════════════════

DURING SUBSCRIPTION: Staff Completes Visit

10. Staff Completes Visit #3
    ├─► UPDATE: Appointment
    │   │  - status: "completed"
    │   └─► completion_photos: [...] (optional)
    │
    ├─► UPDATE: SubscriptionAppointment
    │   └─► status: "completed"
    │
    └─► UPDATE: Subscription
        │  - completed_appointments: 3
        └─► IF completed_appointments == total_appointments:
            └─► status: "completed"
```

---

## Appointment Creation Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ DIRECT APPOINTMENT BOOKING (Single Service)                         │
└─────────────────────────────────────────────────────────────────────┘

[Customer Action]           [Database Operations]              [Validations]

1. Select Service
   └─► READ: Service (is_active=True)
       └─► Get: duration, price, extras

2. Check Staff Availability
   │  - Selected date & time
   │  - Enter postcode
   │
   ├─► READ: StaffArea (postcode coverage)
   │   └─► Filter: Staff with service area covering postcode
   │
   ├─► READ: StaffService (staff assigned to service)
   │
   ├─► READ: StaffSchedule (working hours on selected day)
   │
   └─► READ: Appointment (check staff availability)
       └─► Filter: Overlapping appointments

3. Select Extras (optional)
   └─► e.g., "Inside windows +£10", "High access +£15"

4. Calculate Price
   │  - Base price: £50.00
   │  - Extra 1: +£10.00
   │  - Extra 2: +£15.00
   └─► Total: £75.00

5. Submit Booking
   ├─► CREATE: Appointment
   │   │  - staff: <staff_id>
   │   │  - service: <service_id>
   │   │  - start_time: 2026-02-20 09:00:00
   │   │  - end_time: 2026-02-20 11:00:00 (duration 120 mins)
   │   │  - status: "pending"
   │   │  - appointment_type: "single"
   │   │  - calendar_event_id: {}
   │   └─► calendar_synced_to: []
   │
   └─► CREATE: CustomerAppointment
       │  - customer: <customer_id> OR guest
       │  - appointment: <appointment_id>
       │  - number_of_persons: 1
       │  - extras: [{"name": "Inside windows", "price": 10}]
       │  - total_price: £75.00
       │  - payment_status: "pending"
       │  - cancellation_policy_hours: 24
       │  - can_cancel: True
       │  - can_reschedule: True
       └─► cancellation_deadline: 2026-02-19 09:00:00 (24h before)

6. Sync to Calendar
   └─► IF customer.user.profile.calendar_sync_enabled:
       ├─► Create event in Google/Outlook/Apple Calendar
       └─► UPDATE: Appointment
           │  - calendar_event_id: {"google": "event_456"}
           └─► calendar_synced_to: ["google"]

7. Send Confirmation Email
   └─► Email with appointment details + iCalendar attachment

═══════════════════════════════════════════════════════════════════════

LATER: Customer Cancels Appointment

8. Check Cancellation Policy (24h)
   └─► IF now() < cancellation_deadline:
       ├─► UPDATE: Appointment.status = "cancelled"
       ├─► DELETE: Calendar event (if synced)
       └─► Send cancellation confirmation email
   ELSE:
       └─► Show error: "Cannot cancel within 24h of appointment"
```

---

## User Registration Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ USER REGISTRATION (Different Flows by Role)                          │
└─────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════
CUSTOMER REGISTRATION (Public)
═══════════════════════════════════════════════════════════════════════

1. Customer Submits Form
   │  - Email
   │  - Password
   │  - Name
   │  - Phone (optional)
   └─► Address (optional)

2. Validate Email Unique
   └─► READ: User.objects.filter(email=email).exists()

3. Create User
   ├─► CREATE: User
   │   │  - email: "customer@example.com"
   │   │  - password: <hashed>
   │   │  - role: "customer"
   │   │  - is_verified: False
   │   └─► username: null (optional)
   │
   ├─► CREATE: Profile (auto via post_save signal?)
   │   │  - user: <user_id>
   │   │  - timezone: "Europe/London"
   │   │  - calendar_sync_enabled: False
   │   └─► calendar_provider: "none"
   │
   └─► CREATE: Customer
       │  - user: <user_id>
       │  - name: "John Doe"
       │  - email: "customer@example.com"
       │  - phone: "+44..."
       └─► address fields

4. Send Verification Email
   └─► Email with verification link

5. Customer Clicks Link
   └─► UPDATE: User.is_verified = True

═══════════════════════════════════════════════════════════════════════
STAFF/MANAGER/ADMIN REGISTRATION (Invitation Required)
═══════════════════════════════════════════════════════════════════════

1. Admin Creates Invitation
   ├─► CREATE: Invitation
   │   │  - email: "staff@example.com"
   │   │  - role: "staff"
   │   │  - token: "xyz789..." (auto-generated)
   │   │  - invited_by: <admin_user_id>
   │   │  - expires_at: now() + 7 days (auto-generated)
   │   │  - is_active: True
   │   └─► used_at: null
   │
   └─► Send invitation email with link:
       /register?token=xyz789...

2. Staff Clicks Link
   └─► Validate token:
       ├─► READ: Invitation (token, is_active=True)
       ├─► CHECK: not expired (now() < expires_at)
       └─► CHECK: not used (used_at is null)

3. Staff Submits Registration Form
   │  - Email (must match invitation)
   │  - Password
   │  - Name
   └─► Phone

4. Create User + Staff
   ├─► CREATE: User
   │   │  - email: "staff@example.com"
   │   │  - password: <hashed>
   │   │  - role: "staff"
   │   └─► is_verified: True (auto-verified for staff)
   │
   ├─► CREATE: Profile
   │   │  - user: <user_id>
   │   └─► timezone: "Europe/London"
   │
   ├─► CREATE: Staff
   │   │  - user: <user_id>
   │   │  - name: "Jane Smith"
   │   │  - email: "staff@example.com"
   │   │  - phone: "+44..."
   │   └─► is_active: True
   │
   └─► UPDATE: Invitation
       │  - used_at: now()
       └─► is_active: False

5. Admin Assigns Services & Schedule
   ├─► CREATE: StaffService (staff-service assignments)
   ├─► CREATE: StaffSchedule (working hours)
   └─► CREATE: StaffArea (service coverage)

═══════════════════════════════════════════════════════════════════════
MANAGER REGISTRATION (Similar to Staff)
═══════════════════════════════════════════════════════════════════════

4. Create User + Manager
   ├─► CREATE: User (role="manager")
   ├─► CREATE: Profile
   └─► CREATE: Manager
       │  - user: <user_id>
       │  - can_manage_all: False
       │  - can_manage_customers: False
       │  - can_manage_staff: False
       │  - can_manage_appointments: True
       │  - can_view_reports: True
       └─► permissions: {} (JSON)

5. Admin Assigns Permissions
   └─► UPDATE: Manager
       ├─► managed_staff.add(<staff_id>, <staff_id>...)
       ├─► managed_customers.add(<customer_id>, <customer_id>...)
       └─► can_manage_staff: True
```

---

## Calendar Sync Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ CALENDAR SYNC (Google/Outlook/Apple)                                │
└─────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════
INITIAL CONNECTION: Google Calendar
═══════════════════════════════════════════════════════════════════════

1. User Clicks "Connect Google Calendar"
   └─► Redirect to Google OAuth:
       /api/calendar/google/connect/

2. User Grants Permissions
   └─► Google redirects back with auth_code

3. Backend Exchanges Code for Tokens
   ├─► Request: access_token + refresh_token from Google
   │
   └─► UPDATE: Profile
       │  - calendar_sync_enabled: True
       │  - calendar_provider: "google"
       │  - calendar_access_token: <encrypted>
       │  - calendar_refresh_token: <encrypted>
       └─► calendar_calendar_id: "primary"

4. Sync Existing Appointments
   │
   For each user's appointment:
   │
   ├─► Create event in Google Calendar
   │   │  - Summary: "Window Cleaning - John Doe"
   │   │  - Start: 2026-02-20T09:00:00
   │   │  - End: 2026-02-20T11:00:00
   │   │  - Location: "123 Main St, London SW1A 1AA"
   │   └─► Description: Service details
   │
   └─► UPDATE: Appointment
       │  - calendar_event_id: {"google": "event_789"}
       └─► calendar_synced_to: ["google"]

═══════════════════════════════════════════════════════════════════════
AUTO-SYNC: New Appointment Created
═══════════════════════════════════════════════════════════════════════

5. Order Confirmed (Signal Triggered)
   └─► For each appointment:
       │
       ├─► Check Customer Calendar Sync
       │   └─► IF customer.user.profile.calendar_sync_enabled:
       │       ├─► Create event in customer's calendar
       │       └─► UPDATE: Appointment.calendar_event_id
       │
       ├─► Check Staff Calendar Sync
       │   └─► IF staff.user.profile.calendar_sync_enabled:
       │       ├─► Create event in staff's calendar
       │       └─► UPDATE: Appointment.calendar_event_id
       │
       └─► Check Manager Calendar Sync (if applicable)
           └─► IF manager.user.profile.calendar_sync_enabled:
               ├─► Create event in manager's calendar
               └─► UPDATE: Appointment.calendar_event_id

═══════════════════════════════════════════════════════════════════════
UPDATE: Appointment Rescheduled
═══════════════════════════════════════════════════════════════════════

6. Appointment Time Changed
   ├─► UPDATE: Appointment
   │   │  - start_time: 2026-02-21 14:00:00 (NEW)
   │   └─► end_time: 2026-02-21 16:00:00 (NEW)
   │
   └─► For each synced calendar:
       └─► Update calendar event:
           - event_id: appointment.calendar_event_id["google"]
           - New start/end times

═══════════════════════════════════════════════════════════════════════
DELETE: Appointment Cancelled
═══════════════════════════════════════════════════════════════════════

7. Appointment Cancelled
   ├─► UPDATE: Appointment.status = "cancelled"
   │
   └─► For each synced calendar:
       └─► Delete calendar event:
           - event_id: appointment.calendar_event_id["google"]

═══════════════════════════════════════════════════════════════════════
DISCONNECT: User Disconnects Calendar
═══════════════════════════════════════════════════════════════════════

8. User Clicks "Disconnect Google Calendar"
   ├─► DELETE: All calendar events for user's appointments
   │
   └─► UPDATE: Profile
       │  - calendar_sync_enabled: False
       │  - calendar_provider: "none"
       │  - calendar_access_token: null
       │  - calendar_refresh_token: null
       └─► calendar_calendar_id: null
```

---

## Coupon Application Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ COUPON VALIDATION & APPLICATION                                      │
└─────────────────────────────────────────────────────────────────────┘

[Customer Action]           [Database Operations]              [Validations]

1. Customer Enters Coupon Code
   │  - Code: "SAVE20"
   └─► At checkout

2. Validate Coupon
   ├─► READ: Coupon (code="SAVE20")
   │
   └─► Run: coupon.is_valid(customer, order_amount, service_ids)
       │
       ├─► CHECK: status = "active"
       │   └─► IF NOT: Return "Coupon is not active"
       │
       ├─► CHECK: now() >= valid_from
       │   └─► IF NOT: Return "Coupon not yet valid"
       │
       ├─► CHECK: now() <= valid_until
       │   └─► IF NOT: Return "Coupon has expired"
       │
       ├─► CHECK: used_count < max_uses
       │   └─► IF NOT: Return "Max usage limit reached"
       │
       ├─► CHECK: customer usage < max_uses_per_customer
       │   └─► READ: CouponUsage.filter(coupon, customer).count()
       │   └─► IF NOT: Return "You already used this coupon"
       │
       ├─► CHECK: order_amount >= minimum_order_amount
       │   └─► IF NOT: Return "Minimum order amount £X required"
       │
       ├─► CHECK: Service Restrictions
       │   ├─► IF excluded_services.filter(id__in=service_ids).exists():
       │   │   └─► Return "Coupon not valid for selected services"
       │   │
       │   └─► IF applicable_services.exists():
       │       └─► IF NOT applicable_services.filter(id__in=service_ids).exists():
       │           └─► Return "Coupon doesn't apply to selected services"
       │
       └─► VALID: Return (True, "")

3. Calculate Discount
   └─► Run: coupon.calculate_discount(order_amount)
       │
       ├─► IF discount_type = "percentage":
       │   └─► discount = order_amount × (discount_value / 100)
       │       Example: £150 × (20 / 100) = £30
       │
       └─► IF discount_type = "fixed":
           └─► discount = min(discount_value, order_amount)
               Example: min(£50, £150) = £50

4. Apply to Order
   ├─► Calculate: final_amount = order_amount - discount
   │   Example: £150 - £30 = £120
   │
   └─► UPDATE: Order.total_price = £120

5. Track Usage
   ├─► CREATE: CouponUsage
   │   │  - coupon: <coupon_id>
   │   │  - customer: <customer_id> OR null (guest)
   │   │  - guest_email: "customer@example.com" (if guest)
   │   │  - order: <order_id>
   │   │  - discount_amount: £30.00
   │   │  - order_amount: £150.00
   │   └─► final_amount: £120.00
   │
   └─► UPDATE: Coupon.used_count++
       Example: 5 → 6

═══════════════════════════════════════════════════════════════════════

EXAMPLE COUPONS:

1. "SAVE20" - 20% off all services
   - discount_type: "percentage"
   - discount_value: 20
   - minimum_order_amount: £50
   - max_uses: 100
   - max_uses_per_customer: 1

2. "FIRSTTIME" - £25 off first order
   - discount_type: "fixed"
   - discount_value: 25
   - minimum_order_amount: £75
   - max_uses_per_customer: 1

3. "CLEANSPRING" - 15% off cleaning services only
   - discount_type: "percentage"
   - discount_value: 15
   - applicable_services: [cleaning_service_ids]

4. "NOWINDOW" - 10% off everything except window cleaning
   - discount_type: "percentage"
   - discount_value: 10
   - excluded_services: [window_cleaning_id]
```

---

## Order Confirmation Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ ORDER CONFIRMATION (Admin Action) → Creates Appointments             │
└─────────────────────────────────────────────────────────────────────┘

[Admin Action]              [Database Operations]              [Triggers]

1. Admin Reviews Order
   └─► READ: Order (status="pending")
       └─► Display: Order details, items, customer info

2. Admin Assigns Staff to Items
   └─► For each OrderItem:
       └─► UPDATE: OrderItem.staff = <staff_id>

3. Admin Confirms Order
   └─► UPDATE: Order.status = "confirmed"
       │
       └─► TRIGGER: pre_save signal (orders/signals.py)

═══════════════════════════════════════════════════════════════════════
SIGNAL: on_order_status_changed
═══════════════════════════════════════════════════════════════════════

4. Detect Status Change
   ├─► IF old_status != "confirmed" AND new_status = "confirmed":
   └─► Run: create_appointments_for_order(order)

5. Create Appointments for Each OrderItem
   │
   Example Order:
   │  - Item 1: Window Cleaning (120 mins)
   │  - Item 2: Grass Cutting (60 mins)
   │  - Scheduled: 2026-02-20 09:00
   │
   ├─► ITEM 1: Window Cleaning
   │   │
   │   ├─► CREATE: Appointment
   │   │   │  - staff: <staff_id>
   │   │   │  - service: <window_cleaning_id>
   │   │   │  - start_time: 2026-02-20 09:00:00
   │   │   │  - end_time: 2026-02-20 11:00:00 (09:00 + 120 mins)
   │   │   │  - status: "pending"
   │   │   │  - appointment_type: "order_item"
   │   │   └─► order: <order_id>
   │   │
   │   ├─► UPDATE: OrderItem.appointment = <appointment_id>
   │   │
   │   └─► IF order.customer exists:
   │       └─► CREATE: CustomerAppointment
   │           │  - customer: <customer_id>
   │           │  - appointment: <appointment_id>
   │           │  - total_price: £75.00
   │           │  - payment_status: "pending"
   │           │  - cancellation_policy_hours: 24
   │           │  - can_cancel: True
   │           │  - can_reschedule: True
   │           └─► cancellation_deadline: 2026-02-19 09:00:00
   │
   └─► ITEM 2: Grass Cutting
       │
       ├─► CREATE: Appointment
       │   │  - start_time: 2026-02-20 11:00:00 (after Item 1 ends)
       │   │  - end_time: 2026-02-20 12:00:00 (11:00 + 60 mins)
       │   │  - (+ padding_time if service has it)
       │   └─► Same fields as Item 1
       │
       └─► CREATE: CustomerAppointment (same as Item 1)

6. Sync to Calendars
   └─► Run: sync_order_to_calendars(order)
       │
       For each appointment:
       │
       ├─► CUSTOMER Calendar (if enabled)
       │   │  - IF order.customer.user.profile.calendar_sync_enabled:
       │   │
       │   ├─► Create event in customer's calendar
       │   │   │  - Summary: "Window Cleaning"
       │   │   │  - Start: 2026-02-20 09:00:00
       │   │   │  - End: 2026-02-20 11:00:00
       │   │   │  - Location: <order.address>
       │   │   └─► Description: Service details
       │   │
       │   └─► UPDATE: Appointment
       │       │  - calendar_event_id["google"] = "event_123"
       │       └─► calendar_synced_to.append("google")
       │
       ├─► STAFF Calendar (if enabled)
       │   │  - IF appointment.staff.user.profile.calendar_sync_enabled:
       │   │
       │   ├─► Create event in staff's calendar
       │   │   │  - Summary: "Window Cleaning - John Doe"
       │   │   │  - Start: 2026-02-20 09:00:00
       │   │   │  - End: 2026-02-20 11:00:00
       │   │   │  - Location: <order.address>
       │   │   └─► Description: Customer details, service notes
       │   │
       │   └─► UPDATE: Appointment
       │       │  - calendar_event_id["google"] = "event_456"
       │       └─► calendar_synced_to.append("google")
       │
       └─► MANAGER Calendar (if applicable)
           └─► (Similar to staff calendar)

7. Send Confirmation Email
   └─► Run: send_confirmation_email(order)
       │
       ├─► Email to: order.customer.email OR order.guest_email
       │
       └─► Content:
           - Order confirmed
           - Appointment details (date, time, staff)
           - Tracking link
           - iCalendar attachment
           - Cancellation policy (24h)

═══════════════════════════════════════════════════════════════════════

SUMMARY OF DATABASE WRITES:

For a 2-item order:
- 1× UPDATE: Order.status
- 2× CREATE: Appointment
- 2× UPDATE: OrderItem.appointment
- 2× CREATE: CustomerAppointment (if customer exists)
- 2× UPDATE: Appointment.calendar_event_id (customer sync)
- 2× UPDATE: Appointment.calendar_synced_to (customer sync)
- 2× UPDATE: Appointment.calendar_event_id (staff sync)
- 2× UPDATE: Appointment.calendar_synced_to (staff sync)

Total: 1 UPDATE + 4 CREATES + 8 UPDATES = 13 database operations
```

---

**Last Updated:** 2026-02-15
**Version:** 1.0
**Maintained By:** Development Team
