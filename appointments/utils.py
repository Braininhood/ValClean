"""
Booking utility functions for time slot calculation and availability checking.
"""
from datetime import datetime, timedelta, time
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from .models import Appointment
from staff.models import Staff, StaffScheduleItem, Holiday
from services.models import Service


# Configuration from settings (with defaults)
BOOKING_MIN_TIME_PRIOR_HOURS = getattr(settings, 'BOOKING_MIN_TIME_PRIOR_HOURS', 2)
BOOKING_MAX_DAYS_IN_ADVANCE = getattr(settings, 'BOOKING_MAX_DAYS_IN_ADVANCE', 90)
BOOKING_SLOT_LENGTH_MINUTES = getattr(settings, 'BOOKING_SLOT_LENGTH_MINUTES', 15)


def get_available_time_slots(staff, service, date, timezone_offset=0):
    """
    Get available time slots for a staff member and service on a specific date.
    
    Args:
        staff: Staff instance
        service: Service instance
        date: datetime.date object
        timezone_offset: Client timezone offset in minutes (default: 0)
    
    Returns:
        List of available time slot dictionaries with 'start' and 'end' datetime objects
    """
    # Convert date to datetime for calculations
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d').date()
    
    # Get day of week (0=Monday, 6=Sunday)
    day_index = date.weekday()
    
    # Get staff schedule for this day
    try:
        schedule = StaffScheduleItem.objects.get(staff=staff, day_index=day_index)
    except StaffScheduleItem.DoesNotExist:
        return []  # Staff not available on this day
    
    # Check for holidays
    if is_holiday(staff, date):
        return []
    
    # Calculate service duration including padding
    total_duration = service.duration + service.padding_left + service.padding_right
    
    # Get existing appointments for this date
    start_of_day = timezone.make_aware(datetime.combine(date, time.min))
    end_of_day = timezone.make_aware(datetime.combine(date, time.max))
    
    existing_appointments = Appointment.objects.filter(
        staff=staff,
        start_date__gte=start_of_day,
        start_date__lte=end_of_day
    ).order_by('start_date')
    
    # Get schedule breaks
    breaks = schedule.breaks if schedule.breaks else []
    
    # Generate time slots
    available_slots = []
    current_time = datetime.combine(date, schedule.start_time)
    end_time = datetime.combine(date, schedule.end_time)
    
    # Make timezone-aware
    if timezone.is_naive(current_time):
        current_time = timezone.make_aware(current_time)
    if timezone.is_naive(end_time):
        end_time = timezone.make_aware(end_time)
    
    # Apply timezone offset if provided
    if timezone_offset != 0:
        current_time += timedelta(minutes=timezone_offset)
        end_time += timedelta(minutes=timezone_offset)
    
    while current_time + timedelta(minutes=total_duration) <= end_time:
        slot_start = current_time
        slot_end = current_time + timedelta(minutes=total_duration)
        
        # Check if slot is in a break period
        if is_in_break(slot_start.time(), slot_end.time(), breaks):
            current_time += timedelta(minutes=BOOKING_SLOT_LENGTH_MINUTES)
            continue
        
        # Check if slot conflicts with existing appointments
        if not conflicts_with_appointments(slot_start, slot_end, existing_appointments):
            # Check minimum time prior to booking
            now = timezone.now()
            min_booking_time = now + timedelta(hours=BOOKING_MIN_TIME_PRIOR_HOURS)
            
            if slot_start >= min_booking_time:
                available_slots.append({
                    'start': slot_start,
                    'end': slot_end,
                })
        
        current_time += timedelta(minutes=BOOKING_SLOT_LENGTH_MINUTES)
    
    return available_slots


def is_holiday(staff, date):
    """
    Check if a date is a holiday for the staff member or company-wide.
    
    Args:
        staff: Staff instance
        date: datetime.date object
    
    Returns:
        Boolean indicating if date is a holiday
    """
    # Check for company-wide holidays
    company_holidays = Holiday.objects.filter(
        staff__isnull=True,
        date=date
    )
    if company_holidays.exists():
        return True
    
    # Check for staff-specific holidays
    staff_holidays = Holiday.objects.filter(
        staff=staff,
        date=date
    )
    if staff_holidays.exists():
        return True
    
    # Check for yearly repeating holidays
    year = date.year
    repeating_holidays = Holiday.objects.filter(
        Q(staff__isnull=True) | Q(staff=staff),
        repeat_event=True
    )
    for holiday in repeating_holidays:
        if holiday.date.month == date.month and holiday.date.day == date.day:
            return True
    
    return False


def is_in_break(start_time, end_time, breaks):
    """
    Check if a time slot overlaps with any break periods.
    
    Args:
        start_time: time object
        end_time: time object
        breaks: List of break dictionaries with 'start' and 'end' keys
    
    Returns:
        Boolean indicating if slot is in a break
    """
    for break_period in breaks:
        break_start = datetime.strptime(break_period['start'], '%H:%M').time()
        break_end = datetime.strptime(break_period['end'], '%H:%M').time()
        
        # Check if slot overlaps with break
        if (start_time < break_end and end_time > break_start):
            return True
    
    return False


def conflicts_with_appointments(slot_start, slot_end, existing_appointments):
    """
    Check if a time slot conflicts with existing appointments.
    
    Args:
        slot_start: datetime object
        slot_end: datetime object
        existing_appointments: QuerySet of Appointment objects
    
    Returns:
        Boolean indicating if slot conflicts
    """
    for appointment in existing_appointments:
        # Check if slots overlap
        if (slot_start < appointment.end_date and slot_end > appointment.start_date):
            return True
    
    return False


def get_available_dates(staff, service, start_date=None, days_ahead=None):
    """
    Get list of available dates for booking.
    
    Args:
        staff: Staff instance
        service: Service instance
        start_date: Starting date (default: today)
        days_ahead: Number of days to look ahead (default: BOOKING_MAX_DAYS_IN_ADVANCE)
    
    Returns:
        List of date objects that have available slots
    """
    if start_date is None:
        start_date = timezone.now().date()
    if days_ahead is None:
        days_ahead = BOOKING_MAX_DAYS_IN_ADVANCE
    
    available_dates = []
    current_date = start_date
    end_date = start_date + timedelta(days=days_ahead)
    
    while current_date <= end_date:
        # Skip past dates
        if current_date < timezone.now().date():
            current_date += timedelta(days=1)
            continue
        
        # Check if date has available slots
        slots = get_available_time_slots(staff, service, current_date)
        if slots:
            available_dates.append(current_date)
        
        current_date += timedelta(days=1)
    
    return available_dates


def get_staff_for_service(service):
    """
    Get staff members who offer a specific service.
    
    Args:
        service: Service instance
    
    Returns:
        List of Staff instances
    """
    # Get staff who have this service assigned
    staff_services = service.staff_services.filter(
        staff__is_active=True,
        staff__visibility='public'
    ).select_related('staff')
    
    staff_list = [ss.staff for ss in staff_services]
    
    # If no specific staff assigned, return all active staff
    if not staff_list:
        staff_list = list(Staff.objects.filter(
            is_active=True,
            visibility='public'
        ))
    
    return staff_list


def calculate_appointment_price(service, staff, number_of_persons=1, extras=None):
    """
    Calculate the total price for an appointment.
    
    Args:
        service: Service instance
        staff: Staff instance
        number_of_persons: Number of persons (default: 1)
        extras: List of extra items with prices (default: None)
    
    Returns:
        Decimal total price
    """
    from decimal import Decimal
    
    # Get staff-specific price if available
    try:
        staff_service = service.staff_services.get(staff=staff)
        base_price = staff_service.price if staff_service.price else service.price
    except:
        base_price = service.price
    
    # Calculate base price (multiply by number of persons if applicable)
    total_price = base_price * number_of_persons
    
    # Add extras prices
    if extras:
        for extra in extras:
            if 'price' in extra:
                total_price += Decimal(str(extra['price'])) * extra.get('quantity', 1)
    
    return total_price

