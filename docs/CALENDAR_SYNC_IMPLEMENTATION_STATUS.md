# Calendar Sync Implementation Status

## ✅ Completed Steps

### Step 1: Calendar Sync Service Structure ✓
**File:** `backend/apps/calendar_sync/services.py`

Created base calendar sync service with:
- `CalendarSyncService` - Main service class routing to providers
- `GoogleCalendarService` - Google Calendar API (placeholder - needs OAuth tokens)
- `OutlookCalendarService` - Microsoft Graph API (placeholder - needs OAuth tokens)
- `AppleCalendarService` - .ics file generation (**WORKING** - no API needed)

**Event Data Builders:**
- `build_customer_event_data()` - Event data for customer calendar
- `build_staff_event_data()` - Event data for staff calendar
- `build_manager_event_data()` - Event data for manager calendar

### Step 2: Django Signals for Order Confirmation ✓
**File:** `backend/apps/orders/signals.py`

Created signals that:
- Detect when order status changes to 'confirmed'
- Automatically create `Appointment` records for each `OrderItem`
- Trigger calendar sync for relevant users (customer, staff, manager)

**Key Functions:**
- `on_order_status_changed()` - Signal handler for order status changes
- `create_appointments_for_order()` - Creates appointments from order items
- `sync_order_to_calendars()` - Syncs appointments to user calendars

### Step 3: Signal Wiring ✓
**File:** `backend/apps/orders/apps.py`

Updated `OrdersConfig.ready()` to import signals when app loads.

---

## 🔄 How It Works

### When Order is Confirmed:

1. **Order Status Changes to 'confirmed'**
   - Django signal `pre_save` fires
   - `on_order_status_changed()` handler detects change

2. **Appointments Created**
   - `create_appointments_for_order()` called
   - For each `OrderItem`, creates `Appointment`:
     - `appointment.staff` = from `order_item.staff`
     - `appointment.service` = from `order_item.service`
     - `appointment.start_time` = from `order.scheduled_date` + `order.scheduled_time`
     - `appointment.end_time` = `start_time` + `service.duration`
     - `appointment.order` = link to the `Order`
     - `appointment.status` = 'confirmed'
     - `appointment.appointment_type` = 'order_item'

3. **Calendar Sync Triggered**
   - `sync_order_to_calendars()` called
   - For each appointment, syncs to:
     - **Customer** calendar (if `order.customer.user.profile.calendar_sync_enabled`)
     - **Staff** calendar (if `appointment.staff.user.profile.calendar_sync_enabled`)
     - **Manager** calendar (placeholder - when manager relationship is added)

4. **Calendar Events Created**
   - Event data built by role-specific functions
   - `CalendarSyncService.create_event()` called
   - Event ID stored in `appointment.calendar_event_id[provider]`
   - Provider name added to `appointment.calendar_synced_to[]`

---

## 📊 Current Status by Provider

### ✅ Apple Calendar (.ics files)
**Status:** **WORKING** (no OAuth needed)

- `.ics` file generation implemented
- Can generate .ics content for download/email
- Event ID stored in `appointment.calendar_event_id['apple']`

**Next Steps:**
- Add API endpoint to download .ics files
- Add email attachment option for .ics files

### ⏳ Google Calendar
**Status:** **PLACEHOLDER** (needs OAuth implementation)

**What's Done:**
- Service structure created
- Event data builders ready
- Signal integration ready

**What's Needed:**
1. Install Google API client:
   ```bash
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```
2. OAuth 2.0 flow for Google Calendar
3. Token storage in `profile.calendar_access_token` / `calendar_refresh_token`
4. Google Calendar API calls in `GoogleCalendarService`

**API Endpoints Needed:**
- `POST /api/v1/auth/google-calendar/connect` - OAuth authorization
- `GET /api/v1/auth/google-calendar/callback` - OAuth callback
- `POST /api/v1/auth/google-calendar/disconnect` - Revoke access

### ⏳ Microsoft Outlook
**Status:** **PLACEHOLDER** (needs OAuth implementation)

**What's Done:**
- Service structure created
- Event data builders ready
- Signal integration ready

**What's Needed:**
1. Install Microsoft Graph SDK:
   ```bash
   pip install msal msgraph-sdk
   ```
2. OAuth 2.0 flow for Microsoft Graph
3. Token storage in `profile.calendar_access_token` / `calendar_refresh_token`
4. Microsoft Graph API calls in `OutlookCalendarService`

**API Endpoints Needed:**
- `POST /api/v1/auth/outlook/connect` - OAuth authorization
- `GET /api/v1/auth/outlook/callback` - OAuth callback
- `POST /api/v1/auth/outlook/disconnect` - Revoke access

---

## 🧪 Testing

### Manual Test Steps:

1. **Create an order** (via admin or API)
   - Set `status='pending'`
   - Add order items with staff assigned
   - Set `scheduled_date` and `scheduled_time`

2. **Confirm the order** (change status to 'confirmed')
   - In admin: `http://127.0.0.1:8000/admin/orders/order/{id}/change/`
   - Change status from 'pending' to 'confirmed'
   - Save

3. **Verify appointments created**
   - Check `appointments_appointment` table
   - Should have one appointment per order item
   - `appointment.order_id` should link to the order

4. **Verify calendar sync** (if user has sync enabled)
   - Check `appointment.calendar_event_id` JSON field
   - Check `appointment.calendar_synced_to` JSON array
   - For Apple Calendar, `calendar_event_id['apple']` should have a value

### Expected Database State After Order Confirmation:

```sql
-- Order
orders_order: id=1, status='confirmed', scheduled_date='2026-01-20', ...

-- Order Items (with appointments linked)
orders_orderitem: id=1, order_id=1, service_id=5, staff_id=3, appointment_id=10
orders_orderitem: id=2, order_id=1, service_id=7, staff_id=4, appointment_id=11

-- Appointments (created automatically)
appointments_appointment:
  id=10, staff_id=3, service_id=5, order_id=1,
  calendar_event_id='{"apple": "ics_10_1234567890"}',
  calendar_synced_to='["apple"]'
  
appointments_appointment:
  id=11, staff_id=4, service_id=7, order_id=1,
  calendar_event_id='{"apple": "ics_11_1234567890"}',
  calendar_synced_to='["apple"]'
```

---

## 📝 Next Steps

### Immediate:
1. ✅ **DONE:** Calendar sync service structure
2. ✅ **DONE:** Signal integration for order confirmation
3. ⏳ **TODO:** Implement OAuth 2.0 for Google Calendar
4. ⏳ **TODO:** Implement OAuth 2.0 for Microsoft Outlook
5. ⏳ **TODO:** Add .ics file download endpoint

### Future Enhancements:
- Update calendar events when appointments change
- Delete calendar events when appointments cancelled
- Two-way sync (sync changes from calendar back to system)
- Calendar sync status dashboard
- Bulk sync operations (admin)

---

## 🔍 Key Files

### Backend:
- `backend/apps/calendar_sync/services.py` - Calendar sync service
- `backend/apps/orders/signals.py` - Order confirmation signals
- `backend/apps/orders/apps.py` - Signal wiring

### Database:
- `accounts_profile` - Calendar sync settings per user
- `appointments_appointment` - Calendar event IDs per appointment

---

## ✅ Summary

**What Works Now:**
- Order confirmation triggers appointment creation ✓
- Calendar sync service structure ready ✓
- Apple Calendar .ics generation works ✓
- Signal integration complete ✓

**What Needs OAuth:**
- Google Calendar API integration (needs OAuth tokens)
- Microsoft Outlook API integration (needs OAuth tokens)

**Ready to Test:**
- Confirm an order in admin
- Check if appointments are created
- Check if calendar_event_id is stored (for Apple Calendar)
