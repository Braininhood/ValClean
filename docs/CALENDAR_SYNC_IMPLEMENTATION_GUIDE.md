# Calendar Sync Implementation Guide

## 📊 Current Database Structure (Already Saved to DB)

### ✅ Profile Model (`accounts.Profile`)
**Location:** `backend/apps/accounts/models.py`

Stores calendar sync configuration **per user** (all roles: admin, manager, staff, customer):

```python
calendar_sync_enabled = BooleanField  # Enable/disable sync for this user
calendar_provider = CharField         # 'google', 'outlook', 'apple', 'none'
calendar_access_token = TextField     # OAuth access token (encrypted)
calendar_refresh_token = TextField    # OAuth refresh token (encrypted)
calendar_calendar_id = CharField      # Primary calendar ID to sync to
calendar_sync_settings = JSONField    # Sync preferences: {"auto_sync": true, "sync_direction": "outbound", ...}
```

### ✅ Appointment Model (`appointments.Appointment`)
**Location:** `backend/apps/appointments/models.py`

Stores calendar sync status **per appointment**:

```python
calendar_event_id = JSONField   # {"google": "event_123", "outlook": "event_456", "apple": "event_789"}
calendar_synced_to = JSONField  # ["google", "outlook"] - which calendars this event is synced to
```

---

## 🎯 Implementation Plan: Add Calendar Events When Order Confirmed

### Step 1: Create Calendar Sync Service Module

**File:** `backend/apps/calendar_sync/services.py` (NEW)

This will contain:
- `create_calendar_event(appointment, profile)` - Create event in user's calendar
- `update_calendar_event(appointment, profile)` - Update event when appointment changes
- `delete_calendar_event(appointment, profile)` - Delete event when cancelled
- Helper functions for each provider (Google, Outlook, Apple)

### Step 2: Add Signal/Handler for Order Confirmation

**Option A: Django Signal (Recommended)**
**File:** `backend/apps/orders/signals.py` (NEW)

```python
@receiver(pre_save, sender=Order)
def on_order_status_changed(sender, instance, **kwargs):
    """When order status changes to 'confirmed', create appointments and calendar events."""
    if instance.pk:  # Only for existing orders
        old_order = Order.objects.get(pk=instance.pk)
        if old_order.status != 'confirmed' and instance.status == 'confirmed':
            # Order just confirmed - create appointments for each order item
            create_appointments_for_order(instance)
            # Then sync to calendars for relevant users
            sync_order_to_calendars(instance)
```

**Option B: In Order.save() method**
Add logic directly in `Order.save()` when status changes to 'confirmed'.

### Step 3: Create Appointments from Order Items

When order is confirmed, create `Appointment` records for each `OrderItem`:

```python
def create_appointments_for_order(order):
    """Create Appointment for each OrderItem when order is confirmed."""
    from apps.appointments.models import Appointment
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    for item in order.items.all():
        if not item.appointment:  # Don't create duplicate
            # Calculate start/end time from order.scheduled_date + service duration
            start_time = timezone.make_aware(
                datetime.combine(order.scheduled_date, order.scheduled_time or time(9, 0))
            )
            end_time = start_time + timedelta(minutes=item.service.duration)
            
            appointment = Appointment.objects.create(
                staff=item.staff,  # From order item
                service=item.service,
                start_time=start_time,
                end_time=end_time,
                status='confirmed',
                appointment_type='order_item',
                order=order,  # Link to order
            )
            item.appointment = appointment
            item.save()
```

### Step 4: Sync to Calendars for Relevant Users

**Who should get calendar events when order is confirmed?**

1. **Customer** (if has account + calendar sync enabled)
   - Event: "Service Appointment: {Service Name} with {Staff Name}"
   - Location: Order address
   - Description: Order number, staff contact, notes

2. **Staff** (assigned to order item)
   - Event: "Service: {Service Name} at {Customer Name}'s"
   - Location: Order address
   - Description: Customer contact, order number, special instructions

3. **Manager** (if manager of the staff member)
   - Event: "{Staff Name} - {Service Name} at {Customer Name}'s"
   - Location: Order address
   - Description: Full order details, customer info, staff info

4. **Admin** (optional - if wants to sync all appointments)
   - Same as manager view

```python
def sync_order_to_calendars(order):
    """Sync order appointments to calendars of relevant users."""
    from apps.calendar_sync.services import create_calendar_event
    
    # Get all appointments for this order
    appointments = order.appointments.all()
    
    for appointment in appointments:
        # 1. Sync to CUSTOMER calendar (if has account + sync enabled)
        if order.customer and order.customer.user:
            customer_profile = order.customer.user.profile
            if customer_profile.calendar_sync_enabled:
                event_data = build_customer_event_data(order, appointment)
                create_calendar_event(appointment, customer_profile, event_data)
        
        # 2. Sync to STAFF calendar (if sync enabled)
        if appointment.staff and appointment.staff.user:
            staff_profile = appointment.staff.user.profile
            if staff_profile.calendar_sync_enabled:
                event_data = build_staff_event_data(order, appointment)
                create_calendar_event(appointment, staff_profile, event_data)
        
        # 3. Sync to MANAGER calendar (if manager of staff + sync enabled)
        if appointment.staff and appointment.staff.manager:
            manager_profile = appointment.staff.manager.profile
            if manager_profile and manager_profile.calendar_sync_enabled:
                event_data = build_manager_event_data(order, appointment)
                create_calendar_event(appointment, manager_profile, event_data)
```

---

## 📋 Calendar Event Data by Role

### Customer Event Data

```python
{
    "summary": f"Service: {appointment.service.name}",
    "description": f"""
Order: {order.order_number}
Staff: {appointment.staff.name}
Phone: {appointment.staff.phone or 'N/A'}
Notes: {order.notes or 'None'}
    """.strip(),
    "location": f"{order.address_line1}, {order.city}, {order.postcode}",
    "start": appointment.start_time.isoformat(),
    "end": appointment.end_time.isoformat(),
}
```

### Staff Event Data

```python
{
    "summary": f"{appointment.service.name} at {customer_name}'s",
    "description": f"""
Customer: {customer_name}
Email: {order.customer.email or order.guest_email}
Phone: {order.customer.phone or order.guest_phone or 'N/A'}
Order: {order.order_number}
Special Instructions: {order.notes or 'None'}
Address: {order.address_line1}, {order.city}, {order.postcode}
    """.strip(),
    "location": f"{order.address_line1}, {order.city}, {order.postcode}",
    "start": appointment.start_time.isoformat(),
    "end": appointment.end_time.isoformat(),
}
```

### Manager Event Data

```python
{
    "summary": f"{appointment.staff.name} - {appointment.service.name}",
    "description": f"""
Staff: {appointment.staff.name} ({appointment.staff.phone or 'N/A'})
Customer: {customer_name}
Email: {order.customer.email or order.guest_email}
Phone: {order.customer.phone or order.guest_phone or 'N/A'}
Order: {order.order_number}
Service: {appointment.service.name}
Address: {order.address_line1}, {order.city}, {order.postcode}
Notes: {order.notes or 'None'}
    """.strip(),
    "location": f"{order.address_line1}, {order.city}, {order.postcode}",
    "start": appointment.start_time.isoformat(),
    "end": appointment.end_time.isoformat(),
}
```

---

## 🗄️ What Gets Saved to Database

### When Order is Confirmed:

1. **Appointment records created** (one per OrderItem)
   - `appointment.staff` = from `order_item.staff`
   - `appointment.service` = from `order_item.service`
   - `appointment.start_time` / `end_time` = from `order.scheduled_date` + `service.duration`
   - `appointment.order` = link to the `Order`
   - `appointment.status` = 'confirmed'
   - `appointment.appointment_type` = 'order_item'

2. **OrderItem.appointment** field updated
   - Links each order item to its appointment

3. **Calendar events created** (if user has sync enabled)
   - `appointment.calendar_event_id` = `{"google": "event_123", "outlook": "event_456"}` (saved after API call)
   - `appointment.calendar_synced_to` = `["google", "outlook"]` (saved after API call)

### Example Database State After Order Confirmation:

```sql
-- Order
orders_order: status='confirmed', scheduled_date='2026-01-20', ...

-- Order Items (2 items)
orders_orderitem: order_id=1, service_id=5, staff_id=3, appointment_id=10
orders_orderitem: order_id=1, service_id=7, staff_id=4, appointment_id=11

-- Appointments (2 appointments created)
appointments_appointment:
  id=10, staff_id=3, service_id=5, order_id=1,
  calendar_event_id={"google": "abc123"}, calendar_synced_to=["google"]
  
appointments_appointment:
  id=11, staff_id=4, service_id=7, order_id=1,
  calendar_event_id={"google": "def456"}, calendar_synced_to=["google"]

-- Profile (user calendar sync settings)
accounts_profile:
  user_id=10, calendar_sync_enabled=true, calendar_provider='google',
  calendar_access_token='...', calendar_refresh_token='...', calendar_calendar_id='primary'
```

---

## 🔄 Update & Delete Calendar Events

### When Appointment is Updated:

```python
@receiver(pre_save, sender=Appointment)
def on_appointment_updated(sender, instance, **kwargs):
    """Update calendar events when appointment changes."""
    if instance.pk:
        old_appointment = Appointment.objects.get(pk=instance.pk)
        # Check if time, staff, or service changed
        if (old_appointment.start_time != instance.start_time or
            old_appointment.staff != instance.staff or
            old_appointment.service != instance.service):
            update_calendar_events_for_appointment(instance)
```

### When Appointment is Cancelled:

```python
@receiver(pre_save, sender=Appointment)
def on_appointment_cancelled(sender, instance, **kwargs):
    """Delete calendar events when appointment is cancelled."""
    if instance.pk:
        old_appointment = Appointment.objects.get(pk=instance.pk)
        if old_appointment.status != 'cancelled' and instance.status == 'cancelled':
            delete_calendar_events_for_appointment(instance)
```

---

## ✅ Next Steps

1. **Create calendar sync service** (`backend/apps/calendar_sync/services.py`)
   - Google Calendar API integration
   - Microsoft Graph API (Outlook) integration
   - Apple Calendar (.ics file generation)

2. **Add Django signals** (`backend/apps/orders/signals.py`)
   - Detect order confirmation
   - Create appointments from order items
   - Trigger calendar sync

3. **Test with a confirmed order**
   - Confirm an order via admin
   - Verify appointments created
   - Verify calendar events created (if user has sync enabled)

4. **Add OAuth 2.0 flow** (Week 4, Day 4-5)
   - Google OAuth
   - Outlook OAuth
   - Store tokens in Profile model

---

## 📝 Notes

- **Calendar events are OPTIONAL** - Only created if user has `calendar_sync_enabled=True`
- **Multiple calendars supported** - User can sync to Google, Outlook, and Apple simultaneously
- **Guest orders** - Can still create calendar events for customer if guest_email provided (but no user account needed)
- **Appointment records always created** - Even if calendar sync is disabled, appointments are created for internal tracking
