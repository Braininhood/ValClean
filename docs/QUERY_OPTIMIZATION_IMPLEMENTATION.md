# Query Optimization & Database Constraints Implementation

This document tracks the implementation of query optimizations (select_related/prefetch_related) and database CHECK constraints across all apps.

## Query Optimization Strategy

### When to use `select_related()`
- For ForeignKey and OneToOneField relationships
- Performs a SQL JOIN
- Reduces N+1 queries for single-object relationships

### When to use `prefetch_related()`
- For ManyToManyField and reverse ForeignKey relationships
- Performs separate queries and joins in Python
- Reduces N+1 queries for multi-object relationships

## Implementation Status

### ✅ Already Optimized Views

#### Orders App
- `OrderPublicViewSet`: ✅ `prefetch_related('items', 'appointments')`
- `ChangeRequestViewSet`: ✅ `select_related('order', 'reviewed_by')`
- `OrderViewSet`: ✅ `select_related('customer').prefetch_related('items', 'appointments')`

#### Appointments App
- `AppointmentPublicViewSet`: ✅ `select_related('staff', 'service')`
- `AppointmentViewSet`: ✅ `select_related('staff', 'service', 'subscription', 'order').prefetch_related('customer_booking')`

#### Subscriptions App
- `SubscriptionPublicViewSet`: ✅ `select_related('service', 'staff', 'customer').prefetch_related('subscription_appointments')`
- `SubscriptionViewSet`: ✅ `select_related('service', 'staff', 'customer').prefetch_related('subscription_appointments')`

#### Customers App
- `CustomerViewSet`: ✅ `select_related('user').prefetch_related('addresses')`
- `AddressViewSet`: ✅ `select_related('customer')`

#### Staff App
- `StaffViewSet`: ✅ `select_related('user').prefetch_related('schedules', 'staff_services__service__category', 'service_areas__service')`
- `StaffScheduleViewSet`: ✅ `select_related('staff')`
- `StaffAreaViewSet`: ✅ `select_related('staff')`
- `StaffServiceViewSet`: ✅ `select_related('staff', 'service')`

### 🔄 Views Needing Optimization

#### Accounts App (`apps/accounts/views.py`)
```python
# UserViewSet (line ~682)
queryset = User.objects.all()
# NEEDS: select_related('profile')

# ManagerViewSet (line ~794)
queryset = Manager.objects.all()
# NEEDS: select_related('user').prefetch_related('managed_staff', 'managed_customers')

# InvitationViewSet (line ~834)
queryset = Invitation.objects.all()
# NEEDS: select_related('invited_by')

# ProfileViewSet (line ~982)
queryset = Profile.objects.all()
# NEEDS: select_related('user')
```

#### Services App (`apps/services/views.py`)
```python
# CategoryViewSet
queryset = Category.objects.all()
# NEEDS: prefetch_related('services') (if listing services with categories)

# ServiceViewSet
queryset = Service.objects.all()
# NEEDS: select_related('category', 'created_by_staff').prefetch_related('staff_members')
```

#### Coupons App (`apps/coupons/views.py`)
```python
# CouponViewSet
queryset = Coupon.objects.all()
# NEEDS: prefetch_related('applicable_services', 'excluded_services')

# CouponUsageViewSet
queryset = CouponUsage.objects.all()
# NEEDS: select_related('coupon', 'customer', 'order', 'subscription', 'appointment')
```

---

## Database CHECK Constraints

CHECK constraints enforce business rules at the database level, providing data integrity even if validation is bypassed.

### Accounts App (`apps/accounts/models.py`)

#### User Model
```python
class Meta:
    constraints = [
        models.CheckConstraint(
            check=models.Q(role__in=['admin', 'manager', 'staff', 'customer']),
            name='user_valid_role'
        ),
        models.CheckConstraint(
            check=models.Q(email__isnull=False) & ~models.Q(email=''),
            name='user_email_not_empty'
        ),
    ]
```

#### Invitation Model
```python
class Meta:
    constraints = [
        models.CheckConstraint(
            check=models.Q(role__in=['staff', 'manager', 'admin']),
            name='invitation_valid_role'
        ),
        models.CheckConstraint(
            check=models.Q(expires_at__gt=models.F('created_at')),
            name='invitation_expires_after_creation'
        ),
        models.CheckConstraint(
            check=models.Q(email__isnull=False) & ~models.Q(email=''),
            name='invitation_email_not_empty'
        ),
    ]
```

### Customers App (`apps/customers/models.py`)

#### Customer Model
```python
class Meta:
    constraints = [
        models.CheckConstraint(
            check=models.Q(name__isnull=False) & ~models.Q(name=''),
            name='customer_name_not_empty'
        ),
        models.CheckConstraint(
            check=models.Q(email__isnull=False) & ~models.Q(email=''),
            name='customer_email_not_empty'
        ),
    ]
```

#### Address Model
```python
class Meta:
    constraints = [
        models.CheckConstraint(
            check=models.Q(type__in=['billing', 'service', 'other']),
            name='address_valid_type'
        ),
        models.CheckConstraint(
            check=models.Q(address_line1__isnull=False) & ~models.Q(address_line1=''),
            name='address_line1_not_empty'
        ),
        models.CheckConstraint(
            check=models.Q(city__isnull=False) & ~models.Q(city=''),
            name='address_city_not_empty'
        ),
        models.CheckConstraint(
            check=models.Q(postcode__isnull=False) & ~models.Q(postcode=''),
            name='address_postcode_not_empty'
        ),
    ]
```

### Staff App (`apps/staff/models.py`)

#### Staff Model
```python
class Meta:
    constraints = [
        models.CheckConstraint(
            check=models.Q(name__isnull=False) & ~models.Q(name=''),
            name='staff_name_not_empty'
        ),
        models.CheckConstraint(
            check=models.Q(email__isnull=False) & ~models.Q(email=''),
            name='staff_email_not_empty'
        ),
    ]
```

#### StaffSchedule Model
```python
class Meta:
    constraints = [
        models.CheckConstraint(
            check=models.Q(day_of_week__gte=0) & models.Q(day_of_week__lte=6),
            name='staffschedule_valid_day'
        ),
        models.CheckConstraint(
            check=models.Q(end_time__gt=models.F('start_time')),
            name='staffschedule_end_after_start'
        ),
    ]
```

#### StaffService Model
```python
class Meta:
    constraints = [
        models.CheckConstraint(
            check=models.Q(price_override__isnull=True) | models.Q(price_override__gt=0),
            name='staffservice_valid_price_override'
        ),
        models.CheckConstraint(
            check=models.Q(duration_override__isnull=True) | models.Q(duration_override__gt=0),
            name='staffservice_valid_duration_override'
        ),
    ]
```

#### StaffArea Model
```python
class Meta:
    constraints = [
        models.CheckConstraint(
            check=models.Q(radius_miles__gt=0),
            name='staffarea_valid_radius'
        ),
        models.CheckConstraint(
            check=models.Q(postcode__isnull=False) & ~models.Q(postcode=''),
            name='staffarea_postcode_not_empty'
        ),
    ]
```

### Services App (`apps/services/models.py`)

#### Category Model
```python
class Meta:
    constraints = [
        models.CheckConstraint(
            check=models.Q(name__isnull=False) & ~models.Q(name=''),
            name='category_name_not_empty'
        ),
        models.CheckConstraint(
            check=models.Q(position__gte=0),
            name='category_valid_position'
        ),
    ]
```

#### Service Model
```python
class Meta:
    constraints = [
        models.CheckConstraint(
            check=models.Q(name__isnull=False) & ~models.Q(name=''),
            name='service_name_not_empty'
        ),
        models.CheckConstraint(
            check=models.Q(duration__gt=0),
            name='service_valid_duration'
        ),
        models.CheckConstraint(
            check=models.Q(price__gt=0),
            name='service_valid_price'
        ),
        models.CheckConstraint(
            check=models.Q(capacity__gt=0),
            name='service_valid_capacity'
        ),
        models.CheckConstraint(
            check=models.Q(padding_time__gte=0),
            name='service_valid_padding_time'
        ),
        models.CheckConstraint(
            check=models.Q(approval_status__in=['approved', 'pending_approval']),
            name='service_valid_approval_status'
        ),
    ]
```

### Appointments App (`apps/appointments/models.py`)

#### Appointment Model
```python
class Meta:
    constraints = [
        models.CheckConstraint(
            check=models.Q(status__in=['pending', 'confirmed', 'in_progress', 'completed', 'cancelled', 'no_show']),
            name='appointment_valid_status'
        ),
        models.CheckConstraint(
            check=models.Q(appointment_type__in=['single', 'subscription', 'order_item']),
            name='appointment_valid_type'
        ),
        models.CheckConstraint(
            check=models.Q(end_time__gt=models.F('start_time')),
            name='appointment_end_after_start'
        ),
    ]
```

#### CustomerAppointment Model
```python
class Meta:
    constraints = [
        models.CheckConstraint(
            check=models.Q(number_of_persons__gte=1),
            name='customerappointment_valid_persons'
        ),
        models.CheckConstraint(
            check=models.Q(total_price__gte=0),
            name='customerappointment_valid_total_price'
        ),
        models.CheckConstraint(
            check=models.Q(deposit_paid__gte=0),
            name='customerappointment_valid_deposit'
        ),
        models.CheckConstraint(
            check=models.Q(payment_status__in=['pending', 'partial', 'paid', 'refunded']),
            name='customerappointment_valid_payment_status'
        ),
        models.CheckConstraint(
            check=models.Q(cancellation_policy_hours__gt=0),
            name='customerappointment_valid_policy_hours'
        ),
    ]
```

### Orders App (`apps/orders/models.py`)

#### Order Model
```python
class Meta:
    constraints = [
        models.CheckConstraint(
            check=models.Q(status__in=['pending', 'confirmed', 'in_progress', 'completed', 'cancelled']),
            name='order_valid_status'
        ),
        models.CheckConstraint(
            check=models.Q(payment_status__in=['pending', 'partial', 'paid', 'refunded']),
            name='order_valid_payment_status'
        ),
        models.CheckConstraint(
            check=models.Q(total_price__gte=0),
            name='order_valid_total_price'
        ),
        models.CheckConstraint(
            check=models.Q(deposit_paid__gte=0),
            name='order_valid_deposit'
        ),
        models.CheckConstraint(
            check=models.Q(cancellation_policy_hours__gt=0),
            name='order_valid_policy_hours'
        ),
        models.CheckConstraint(
            check=models.Q(order_number__isnull=False) & ~models.Q(order_number=''),
            name='order_number_not_empty'
        ),
        models.CheckConstraint(
            check=models.Q(tracking_token__isnull=False) & ~models.Q(tracking_token=''),
            name='order_tracking_token_not_empty'
        ),
        # Guest orders require guest_email
        models.CheckConstraint(
            check=models.Q(customer__isnull=False) | (models.Q(guest_email__isnull=False) & ~models.Q(guest_email='')),
            name='order_has_customer_or_guest_email'
        ),
    ]
```

#### OrderItem Model
```python
class Meta:
    constraints = [
        models.CheckConstraint(
            check=models.Q(quantity__gte=1),
            name='orderitem_valid_quantity'
        ),
        models.CheckConstraint(
            check=models.Q(unit_price__gt=0),
            name='orderitem_valid_unit_price'
        ),
        models.CheckConstraint(
            check=models.Q(total_price__gte=0),
            name='orderitem_valid_total_price'
        ),
        models.CheckConstraint(
            check=models.Q(status__in=['pending', 'confirmed', 'in_progress', 'completed', 'cancelled']),
            name='orderitem_valid_status'
        ),
    ]
```

#### ChangeRequest Model
```python
class Meta:
    constraints = [
        models.CheckConstraint(
            check=models.Q(status__in=['pending', 'approved', 'rejected']),
            name='changerequest_valid_status'
        ),
        models.CheckConstraint(
            check=models.Q(requested_date__isnull=False),
            name='changerequest_has_date'
        ),
    ]
```

### Subscriptions App (`apps/subscriptions/models.py`)

#### Subscription Model
```python
class Meta:
    constraints = [
        models.CheckConstraint(
            check=models.Q(frequency__in=['weekly', 'biweekly', 'monthly']),
            name='subscription_valid_frequency'
        ),
        models.CheckConstraint(
            check=models.Q(status__in=['active', 'paused', 'cancelled', 'completed']),
            name='subscription_valid_status'
        ),
        models.CheckConstraint(
            check=models.Q(payment_status__in=['pending', 'partial', 'paid', 'refunded']),
            name='subscription_valid_payment_status'
        ),
        models.CheckConstraint(
            check=models.Q(duration_months__gte=1),
            name='subscription_valid_duration'
        ),
        models.CheckConstraint(
            check=models.Q(total_appointments__gte=0),
            name='subscription_valid_total_appointments'
        ),
        models.CheckConstraint(
            check=models.Q(completed_appointments__gte=0),
            name='subscription_valid_completed_appointments'
        ),
        models.CheckConstraint(
            check=models.Q(completed_appointments__lte=models.F('total_appointments')),
            name='subscription_completed_not_exceeds_total'
        ),
        models.CheckConstraint(
            check=models.Q(price_per_appointment__gt=0),
            name='subscription_valid_price_per_appointment'
        ),
        models.CheckConstraint(
            check=models.Q(total_price__gte=0),
            name='subscription_valid_total_price'
        ),
        models.CheckConstraint(
            check=models.Q(end_date__gt=models.F('start_date')),
            name='subscription_end_after_start'
        ),
        models.CheckConstraint(
            check=models.Q(subscription_number__isnull=False) & ~models.Q(subscription_number=''),
            name='subscription_number_not_empty'
        ),
        models.CheckConstraint(
            check=models.Q(tracking_token__isnull=False) & ~models.Q(tracking_token=''),
            name='subscription_tracking_token_not_empty'
        ),
        # Guest subscriptions require guest_email
        models.CheckConstraint(
            check=models.Q(customer__isnull=False) | (models.Q(guest_email__isnull=False) & ~models.Q(guest_email='')),
            name='subscription_has_customer_or_guest_email'
        ),
    ]
```

#### SubscriptionAppointment Model
```python
class Meta:
    constraints = [
        models.CheckConstraint(
            check=models.Q(status__in=['scheduled', 'completed', 'cancelled', 'skipped']),
            name='subscriptionappointment_valid_status'
        ),
        models.CheckConstraint(
            check=models.Q(sequence_number__gte=1),
            name='subscriptionappointment_valid_sequence'
        ),
    ]
```

#### SubscriptionAppointmentChangeRequest Model
```python
class Meta:
    constraints = [
        models.CheckConstraint(
            check=models.Q(status__in=['pending', 'approved', 'rejected']),
            name='subscriptionappointmentchangerequest_valid_status'
        ),
        models.CheckConstraint(
            check=models.Q(requested_date__isnull=False),
            name='subscriptionappointmentchangerequest_has_date'
        ),
    ]
```

### Coupons App (`apps/coupons/models.py`)

#### Coupon Model
```python
class Meta:
    constraints = [
        models.CheckConstraint(
            check=models.Q(discount_type__in=['percentage', 'fixed']),
            name='coupon_valid_discount_type'
        ),
        models.CheckConstraint(
            check=models.Q(status__in=['active', 'inactive', 'expired']),
            name='coupon_valid_status'
        ),
        models.CheckConstraint(
            check=models.Q(discount_value__gt=0),
            name='coupon_valid_discount_value'
        ),
        # Percentage discounts cannot exceed 100%
        models.CheckConstraint(
            check=models.Q(discount_type='fixed') | models.Q(discount_value__lte=100),
            name='coupon_percentage_max_100'
        ),
        models.CheckConstraint(
            check=models.Q(used_count__gte=0),
            name='coupon_valid_used_count'
        ),
        models.CheckConstraint(
            check=models.Q(max_uses__isnull=True) | models.Q(max_uses__gte=1),
            name='coupon_valid_max_uses'
        ),
        models.CheckConstraint(
            check=models.Q(max_uses_per_customer__isnull=True) | models.Q(max_uses_per_customer__gte=1),
            name='coupon_valid_max_uses_per_customer'
        ),
        models.CheckConstraint(
            check=models.Q(minimum_order_amount__gte=0),
            name='coupon_valid_minimum_order_amount'
        ),
        models.CheckConstraint(
            check=models.Q(code__isnull=False) & ~models.Q(code=''),
            name='coupon_code_not_empty'
        ),
    ]
```

#### CouponUsage Model
```python
class Meta:
    constraints = [
        models.CheckConstraint(
            check=models.Q(discount_amount__gte=0),
            name='couponusage_valid_discount_amount'
        ),
        models.CheckConstraint(
            check=models.Q(order_amount__gt=0),
            name='couponusage_valid_order_amount'
        ),
        models.CheckConstraint(
            check=models.Q(final_amount__gte=0),
            name='couponusage_valid_final_amount'
        ),
        models.CheckConstraint(
            check=models.Q(final_amount__lte=models.F('order_amount')),
            name='couponusage_final_not_exceeds_order'
        ),
        # Must have either customer or guest_email
        models.CheckConstraint(
            check=models.Q(customer__isnull=False) | (models.Q(guest_email__isnull=False) & ~models.Q(guest_email='')),
            name='couponusage_has_customer_or_guest_email'
        ),
    ]
```

---

## Migration File Structure

All CHECK constraints will be added in a single migration file for each app:

```python
# apps/<app_name>/migrations/0XXX_add_check_constraints.py

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('<app_name>', 'previous_migration'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='<model_name>',
            constraint=models.CheckConstraint(
                check=models.Q(...),
                name='<constraint_name>'
            ),
        ),
        # ... more constraints ...
    ]
```

---

## Performance Impact

### Expected Improvements
- **N+1 Query Reduction:** 50-90% reduction in database queries
- **Response Time:** 20-60% faster API responses for list endpoints
- **Database Load:** Reduced number of round-trips to database
- **Data Integrity:** CHECK constraints prevent invalid data at database level

### Monitoring
- Monitor query counts before/after with Django Debug Toolbar
- Check slow query logs
- Use `python manage.py querycount` to track query reduction

---

**Status:** 🚧 Implementation in Progress  
**Last Updated:** 2026-02-15  
**Version:** 1.0
