# Order Data Documentation

This document shows what information is saved to the database after booking completion, what's visible in the admin panel, and what happens when deleting records.

## 1️⃣ Data Saved to Database After Booking

When a customer completes a booking, the following data is saved to the database:

### Order Table (`orders_order`)

| Field | Value | Description |
|-------|-------|-------------|
| `id` | Auto-generated | Unique order ID |
| `order_number` | `ORD-YYYYMMDD-XXXXXX` | Unique order number (e.g., `ORD-20260117-ABC123`) |
| `tracking_token` | Random token | Unique tracking token for guest order access |
| `customer_id` | `NULL` or `customer.id` | Customer FK (NULL for guest orders, linked after login/registration) |
| `is_guest_order` | `true` or `false` | Flag for guest orders |
| `account_linked_at` | `NULL` or timestamp | When guest order was linked to customer account |
| `guest_email` | Email string | Email for guest orders |
| `guest_name` | Name string | Name for guest orders |
| `guest_phone` | Phone string | Phone for guest orders |
| `status` | `'pending'` | Order status (pending, confirmed, in_progress, completed, cancelled) |
| `payment_status` | `'pending'` | Payment status (pending, partial, paid, refunded) |
| `total_price` | Decimal | Total order price (e.g., `50.00`) |
| `deposit_paid` | `0` | Deposit amount paid (default: 0) |
| `scheduled_date` | Date | Preferred service date (e.g., `2026-01-20`) |
| `scheduled_time` | Time | Preferred service time (e.g., `15:30:00`) |
| `cancellation_policy_hours` | `24` | Cancellation policy hours (default: 24) |
| `can_cancel` | Boolean | Can cancel this order (auto-calculated) |
| `can_reschedule` | Boolean | Can reschedule this order (auto-calculated) |
| `cancellation_deadline` | DateTime | Deadline for cancellation/rescheduling (auto-calculated) |
| `address_line1` | String | Service address line 1 |
| `address_line2` | String or `NULL` | Service address line 2 (optional) |
| `city` | String | City |
| `postcode` | String | Postcode (UK format) |
| `country` | `'United Kingdom'` | Country (default: UK) |
| `notes` | Text or `NULL` | Customer notes or special instructions |
| `created_at` | DateTime | Order creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

### OrderItem Table (`orders_orderitem`)

For each service in the order, an OrderItem record is created:

| Field | Value | Description |
|-------|-------|-------------|
| `id` | Auto-generated | Unique order item ID |
| `order_id` | `order.id` | Order FK |
| `service_id` | `service.id` | Service FK |
| `staff_id` | `staff.id` or `NULL` | Staff FK (NULL if auto-assigned) |
| `quantity` | Integer | Quantity (default: 1) |
| `unit_price` | Decimal | Service price per unit |
| `total_price` | Decimal | `unit_price * quantity` |
| `status` | `'pending'` | Item status |
| `appointment_id` | `NULL` | Appointment FK (created when order is confirmed) |
| `notes` | `NULL` | Item-specific notes |
| `created_at` | DateTime | Item creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

### Customer Table (`customers_customer`)

If a customer is found/created during booking:

| Field | Value | Description |
|-------|-------|-------------|
| `id` | Auto-generated | Customer ID |
| `user_id` | `NULL` or `user.id` | User FK (NULL for guest customers) |
| `email` | Email string | Customer email |
| `name` | Name string | Customer name |
| `phone` | Phone string or `NULL` | Customer phone |
| `address_line1`, `address_line2`, `city`, `postcode`, `country` | Address fields | Customer address (nullable) |

---

## 2️⃣ What's Visible in Admin Panel

### Order List View (`/admin/orders/order/`)

The admin shows the following columns:

1. **Order Number** - `ORD-YYYYMMDD-XXXXXX`
2. **Customer / Guest** - Shows customer name OR "Guest Name (email@example.com)"
3. **Total Price** - `£50.00`
4. **Status** - `pending`, `confirmed`, `in_progress`, `completed`, `cancelled`
5. **Payment Status** - `pending`, `partial`, `paid`, `refunded`
6. **Is Guest Order** - ✓ or empty checkbox
7. **Created At** - Timestamp

### Order Detail View (`/admin/orders/order/{id}/change/`)

When you click on an order, you see organized fieldsets:

#### 📦 Order Information
- **Order Number** (read-only) - Auto-generated unique number
- **Tracking Token** (read-only) - For guest order access
- **Customer** (dropdown) - Can link/change customer
- **Is Guest Order** (checkbox) - Guest order flag
- **Account Linked At** (read-only) - Timestamp when linked

#### 👤 Guest Information
- **Guest Email** - Email for guest orders
- **Guest Name** - Name for guest orders
- **Guest Phone** - Phone for guest orders

#### 📊 Order Status
- **Status** (dropdown) - Order status
- **Payment Status** (dropdown) - Payment status
- **Total Price** - Order total
- **Deposit Paid** - Deposit amount

#### 📅 Scheduling
- **Scheduled Date** - Service date
- **Scheduled Time** - Service time

#### ⏰ Cancellation Policy
- **Cancellation Policy Hours** - Hours (default: 24)
- **Cancellation Deadline** (read-only) - Auto-calculated
- **Can Cancel** (read-only) - Boolean
- **Can Reschedule** (read-only) - Boolean

#### 📍 Service Address
- **Address Line 1** - Street address
- **Address Line 2** - Optional
- **City** - City
- **Postcode** - UK postcode
- **Country** - Country (default: United Kingdom)
- **Notes** - Customer notes

#### 🕒 Timestamps
- **Created At** (read-only)
- **Updated At** (read-only)

#### 📋 Inline Order Items
Below the main form, you see **OrderItem** records:
- **Service** (autocomplete)
- **Staff** (autocomplete)
- **Quantity**
- **Unit Price**
- **Total Price**
- **Status**
- **Appointment** (if created)

---

## 3️⃣ Delete Behavior (What Gets Deleted from DB)

### Deleting an Order from Admin

When you delete an Order from `/admin/orders/order/{id}/delete/`:

#### ✅ DELETED:
- **Order record** - The order itself is deleted
- **OrderItem records** - All items in the order are cascade deleted (because `OrderItem.order` has `on_delete=models.CASCADE`)

#### ❌ NOT DELETED (Remains in DB):
- **Customer record** - Order.customer FK uses `on_delete=models.SET_NULL`, so:
  - Customer record stays in database
  - Order's `customer_id` would be set to NULL (but order is deleted anyway)
- **Service records** - OrderItem.service FK - services are not deleted
- **Staff records** - OrderItem.staff FK - staff are not deleted

#### ⚠️ RELATED RECORDS (Check FK Behavior):
- **Appointment records** - `Appointment.order` has `on_delete=models.SET_NULL`:
  - **Appointments WILL REMAIN** in database
  - **`order_id` will be set to NULL** in appointments
  - Appointments become "orphaned" (not linked to any order)

### Deleting an OrderItem from Admin

When you delete an OrderItem from inline admin:

#### ✅ DELETED:
- **OrderItem record** - The item itself

#### ❌ NOT DELETED:
- **Order record** - Order remains
- **Service record** - Service remains
- **Staff record** - Staff remains
- **Appointment record** - If linked, appointment.order_id is set to NULL (due to `on_delete=models.SET_NULL`)

### Deleting a Customer from Admin

When you delete a Customer from `/admin/customers/customer/{id}/delete/`:

#### ✅ DELETED:
- **Customer record** - The customer itself

#### ⚠️ RELATED ORDERS:
- **Order records** - `Order.customer` has `on_delete=models.SET_NULL`:
  - **Orders WILL REMAIN** in database
  - **`customer_id` is set to NULL** in orders
  - Orders become guest orders (customer_id = NULL)
  - Guest email/name/phone remain (if they exist)

---

## 🔍 Database Relationships

### Foreign Key Behaviors:

| Relationship | FK Field | on_delete | Behavior |
|--------------|----------|-----------|----------|
| Order → Customer | `Order.customer` | `SET_NULL` | If customer deleted, order.customer_id = NULL |
| OrderItem → Order | `OrderItem.order` | `CASCADE` | If order deleted, items are deleted |
| OrderItem → Service | `OrderItem.service` | `CASCADE` | If service deleted, items are deleted |
| OrderItem → Staff | `OrderItem.staff` | `CASCADE` | If staff deleted, items are deleted |
| Appointment → Order | `Appointment.order` | `SET_NULL` | If order deleted, appointment.order_id = NULL |
| Customer → User | `Customer.user` | `SET_NULL` | If user deleted, customer.user_id = NULL |

---

## 🔍 Summary: What You See in Admin

### Order List View (`/admin/orders/order/`)

When you view the order list, you now see:

| Column | Example | Description |
|--------|---------|-------------|
| **Order Number** | `ORD-20260117-ABC123` | Unique order identifier |
| **Customer / Guest** | `John Doe` or `Guest (email@example.com)` | Customer name or guest info |
| **Total Price** | `£50.00` | Order total |
| **Status** | `pending` | Order status |
| **Payment Status** | `pending` | Payment status |
| **Is Guest Order** | ✓ or empty | Guest order flag |
| **Scheduled** | `2026-01-20 15:30` | Scheduled date and time |
| **Items** | `1` | Number of items in order |
| **Created At** | `2026-01-17 21:20:42` | Creation timestamp |

### Order Detail View (Click on Order)

All fields are organized in collapsible sections:

1. **📦 Order Information** - Order number, tracking token, customer, guest flags
2. **👤 Guest Information** - Guest email, name, phone (for guest orders)
3. **📊 Order Status** - Status, payment status, prices
4. **📅 Scheduling** - Scheduled date and time
5. **⏰ Cancellation Policy** - Cancellation rules and deadlines
6. **📍 Service Address** - Full address details (collapsed by default)
7. **🕒 Timestamps** - Created/updated times (collapsed by default)
8. **📋 Inline Order Items** - All services in the order (below form)

---

## 🗑️ Delete Behavior: Detailed Breakdown

### Scenario 1: Delete Order from Admin

**Action:** Click "Delete" on order `/admin/orders/order/{id}/delete/`

**What Gets Deleted:**
- ✅ **Order** record (main order)
- ✅ **OrderItem** records (all items in order - CASCADE delete)

**What Remains (NOT Deleted):**
- ❌ **Customer** record - Stays in database
  - `Order.customer` FK has `on_delete=models.SET_NULL`
  - If customer deleted separately, order.customer_id becomes NULL
- ❌ **Service** records - Stays in database
- ❌ **Staff** records - Stays in database

**What Happens to Related:**
- ⚠️ **Appointment** records:
  - **WILL REMAIN** in database
  - `Appointment.order` FK has `on_delete=models.SET_NULL`
  - `appointment.order_id` will be set to `NULL`
  - Appointments become "orphaned" (not linked to any order)
  - **You can still see them** in `/admin/appointments/appointment/`
  - **They still exist** but `order_id = NULL`

### Scenario 2: Delete OrderItem from Inline Admin

**Action:** Delete an OrderItem from the inline form

**What Gets Deleted:**
- ✅ **OrderItem** record only

**What Remains:**
- ❌ **Order** - Still exists
- ❌ **Service** - Still exists
- ❌ **Staff** - Still exists

**What Happens to Related:**
- ⚠️ **Appointment** (if linked):
  - **WILL REMAIN** in database
  - `OrderItem.appointment` FK has `on_delete=models.SET_NULL`
  - `orderitem.appointment_id` set to NULL
  - **Appointment stays linked to Order** (if Order still exists)
  - Only the link between OrderItem and Appointment is broken

### Scenario 3: Delete Customer from Admin

**Action:** Delete customer from `/admin/customers/customer/{id}/delete/`

**What Gets Deleted:**
- ✅ **Customer** record

**What Happens to Orders:**
- ⚠️ **All Orders linked to this customer:**
  - **Orders WILL REMAIN** in database
  - `Order.customer` FK has `on_delete=models.SET_NULL`
  - `order.customer_id` set to `NULL`
  - Orders become "guest orders" (customer_id = NULL)
  - Guest email/name/phone remain (if they exist)
  - `is_guest_order` may need manual update to `True`

---

## 🧪 How to Verify This Data

### Option 1: Run Verification Script

```bash
cd backend
python manage.py shell < verify_order_data.py
```

### Option 2: Check Admin Panel

1. Go to `/admin/orders/order/` to see all orders
2. Click on any order to see full details
3. Check inline OrderItems below the form
4. Try deleting an order and check what happens

### Option 3: Database Query

```python
from apps.orders.models import Order, OrderItem
from django.db.models import Q

# Get latest order
order = Order.objects.select_related('customer').prefetch_related('items', 'appointments').order_by('-created_at').first()

# Print all fields
print(f"Order: {order.order_number}")
print(f"Customer: {order.customer}")
print(f"Guest Email: {order.guest_email}")
print(f"Items: {order.items.count()}")
print(f"Appointments: {order.appointments.count()}")
```

---

## 📝 Example: What Gets Saved

When a customer books "Window Cleaning" service:

**Database Records Created:**

1. **Order** record:
   - `order_number`: `ORD-20260117-ABC123`
   - `tracking_token`: `xyz789...`
   - `customer_id`: `NULL` (if guest) or `1` (if customer exists)
   - `guest_email`: `customer@example.com`
   - `guest_name`: `John Doe`
   - `guest_phone`: `07123456789`
   - `total_price`: `50.00`
   - `scheduled_date`: `2026-01-20`
   - `scheduled_time`: `15:30:00`
   - `address_line1`: `10 Downing Street`
   - `city`: `London`
   - `postcode`: `SW1A 1AA`
   - etc.

2. **OrderItem** record:
   - `order_id`: `1` (points to Order)
   - `service_id`: `2` (Window Cleaning service)
   - `staff_id`: `1` (assigned staff or NULL)
   - `quantity`: `1`
   - `unit_price`: `50.00`
   - `total_price`: `50.00`

3. **Customer** record (if new customer):
   - `email`: `customer@example.com`
   - `name`: `John Doe`
   - `phone`: `07123456789`
   - `user_id`: `NULL` (no user account)

4. **Appointment** record (created later when order is confirmed):
   - `order_id`: `1`
   - `service_id`: `2`
   - `staff_id`: `1`
   - `start_time`: `2026-01-20 15:30:00`
   - `end_time`: `2026-01-20 16:00:00`
   - `status`: `pending`

---

## ✅ Summary

- **All booking information is saved** to `orders_order` table (customer info, address, scheduling, pricing)
- **Each service in order** creates an `OrderItem` record
- **Admin panel shows** all order details, organized in fieldsets
- **Deleting order** deletes order + items, but **keeps** customer, services, staff
- **Deleting order** sets `Appointment.order_id` to NULL (appointments remain)
