"""
Booking views for multi-step appointment booking process.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from datetime import datetime, timedelta, date
from decimal import Decimal
import calendar
import logging
import base64

logger = logging.getLogger(__name__)

from services.models import Service, Category
from staff.models import Staff
from customers.models import Customer
from .models import Appointment, CustomerAppointment
from .utils import (
    get_available_time_slots,
    get_available_dates,
    get_staff_for_service,
    calculate_appointment_price,
)

# Session keys for booking flow
SESSION_KEY_BOOKING = 'booking_data'
SESSION_KEY_BOOKING_STEP = 'booking_step'


def clear_booking_session(request):
    """Clear booking session data."""
    if SESSION_KEY_BOOKING in request.session:
        del request.session[SESSION_KEY_BOOKING]
    if SESSION_KEY_BOOKING_STEP in request.session:
        del request.session[SESSION_KEY_BOOKING_STEP]
    request.session.save()


def get_booking_data(request):
    """Get booking data from session."""
    return request.session.get(SESSION_KEY_BOOKING, {})


def save_booking_data(request, data):
    """Save booking data to session."""
    booking_data = get_booking_data(request)
    booking_data.update(data)
    request.session[SESSION_KEY_BOOKING] = booking_data
    request.session.save()


@login_required
def booking_step1_service(request):
    """Step 1: Service Selection"""
    from appointments.utils import get_staff_for_service
    
    categories = Category.objects.filter(is_active=True, visibility='public')
    services = Service.objects.filter(is_active=True, visibility='public')
    
    # Filter by category if provided
    category_id = request.GET.get('category')
    if category_id:
        services = services.filter(category_id=category_id)
    
    # Pre-select service if provided in URL
    selected_service_id = request.GET.get('service_id')
    
    # Get all available staff for display
    all_staff = Staff.objects.filter(is_active=True)
    
    context = {
        'categories': categories,
        'services': services,
        'selected_service_id': selected_service_id,
        'all_staff': all_staff,
    }
    
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        staff_id = request.POST.get('staff_id', '')
        number_of_persons = int(request.POST.get('number_of_persons', 1))
        
        if not service_id:
            messages.error(request, 'Please select a service.')
            return render(request, 'appointments/booking_step1_service.html', context)
        
        try:
            service = Service.objects.get(id=service_id, is_active=True)
        except Service.DoesNotExist:
            messages.error(request, 'Invalid service selected.')
            return render(request, 'appointments/booking_step1_service.html', context)
        
        # Save to session
        save_booking_data(request, {
            'service_id': service_id,
            'staff_id': staff_id if staff_id else None,
            'number_of_persons': number_of_persons,
        })
        request.session[SESSION_KEY_BOOKING_STEP] = 1
        
        # Move to next step
        return redirect('appointments:booking_step2_extras')
    
    return render(request, 'appointments/booking_step1_service.html', context)


@login_required
def booking_step2_extras(request):
    """Step 2: Extras Selection (Optional)"""
    booking_data = get_booking_data(request)
    
    if 'service_id' not in booking_data:
        messages.error(request, 'Please start from the beginning.')
        return redirect('appointments:booking_step1_service')
    
    try:
        service = Service.objects.get(id=booking_data['service_id'])
    except Service.DoesNotExist:
        messages.error(request, 'Service not found.')
        return redirect('appointments:booking_step1_service')
    
    context = {
        'service': service,
    }
    
    if request.method == 'POST':
        # TODO: Implement extras when Extras model is created
        request.session[SESSION_KEY_BOOKING_STEP] = 2
        return redirect('appointments:booking_step3_time')
    
    return render(request, 'appointments/booking_step2_extras.html', context)


@login_required
def booking_step3_time(request):
    """Step 3: Time Selection"""
    booking_data = get_booking_data(request)
    
    if 'service_id' not in booking_data:
        messages.error(request, 'Please start from the beginning.')
        return redirect('appointments:booking_step1_service')
    
    try:
        service = Service.objects.get(id=booking_data['service_id'])
    except Service.DoesNotExist:
        messages.error(request, 'Service not found.')
        return redirect('appointments:booking_step1_service')
    
    # Get staff
    staff_id = booking_data.get('staff_id')
    staff = None
    if staff_id:
        try:
            staff = Staff.objects.get(id=staff_id, is_active=True)
        except Staff.DoesNotExist:
            staff = None
    
    if not staff:
        staff_list = get_staff_for_service(service)
        staff = staff_list[0] if staff_list else None
    
    if not staff:
        messages.error(request, 'No staff available for this service.')
        return redirect('appointments:booking_step1_service')
    
    # Ensure staff_id is saved in session
    if booking_data.get('staff_id') != str(staff.id):
        save_booking_data(request, {'staff_id': str(staff.id)})
    
    # Get selected date
    selected_date = request.GET.get('date')
    if selected_date:
        try:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()
    
    # Get available dates
    available_dates = get_available_dates(staff, service)
    
    # Get available time slots for selected date
    time_slots = get_available_time_slots(staff, service, selected_date)
    
    context = {
        'service': service,
        'staff': staff,
        'selected_date': selected_date,
        'available_dates': available_dates,
        'time_slots': time_slots,
    }
    
    if request.method == 'POST':
        selected_time = request.POST.get('selected_time')
        if not selected_time:
            messages.error(request, 'Please select a time slot.')
            return render(request, 'appointments/booking_step3_time.html', context)
        
        try:
            if 'T' in selected_time:
                start_datetime = datetime.fromisoformat(selected_time.replace('Z', '+00:00'))
            else:
                start_datetime = datetime.strptime(selected_time, '%Y-%m-%d %H:%M:%S')
            
            if timezone.is_naive(start_datetime):
                start_datetime = timezone.make_aware(start_datetime)
            
            end_datetime = start_datetime + timedelta(minutes=service.duration)
            
            save_booking_data(request, {
                'start_datetime': start_datetime.isoformat(),
                'end_datetime': end_datetime.isoformat(),
            })
            request.session[SESSION_KEY_BOOKING_STEP] = 3
            return redirect('appointments:booking_step4_repeat')
        except Exception as e:
            messages.error(request, f'Invalid time selected: {str(e)}')
            return render(request, 'appointments/booking_step3_time.html', context)
    
    return render(request, 'appointments/booking_step3_time.html', context)


@login_required
def booking_step4_repeat(request):
    """Step 4: Repeat Selection (Optional - Recurring Appointments)"""
    booking_data = get_booking_data(request)
    
    if 'start_datetime' not in booking_data:
        messages.error(request, 'Please start from the beginning.')
        return redirect('appointments:booking_step1_service')
    
    try:
        service = Service.objects.get(id=booking_data['service_id'])
        staff = Staff.objects.get(id=booking_data.get('staff_id'))
    except (Service.DoesNotExist, Staff.DoesNotExist):
        messages.error(request, 'Invalid booking data.')
        return redirect('appointments:booking_step1_service')
    
    # Parse datetime
    start_datetime_str = booking_data.get('start_datetime')
    if not start_datetime_str:
        messages.error(request, 'Booking start time is missing.')
        return redirect('appointments:booking_step3_time')
    
    try:
        if isinstance(start_datetime_str, str):
            try:
                start_datetime = datetime.fromisoformat(start_datetime_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                try:
                    start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%dT%H:%M:%S%z')
                except:
                    start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%dT%H:%M:%S')
        else:
            start_datetime = start_datetime_str
        
        if isinstance(start_datetime, datetime) and timezone.is_naive(start_datetime):
            start_datetime = timezone.make_aware(start_datetime)
    except Exception as e:
        messages.error(request, f'Invalid datetime format in session: {str(e)}')
        return redirect('appointments:booking_step3_time')
    
    context = {
        'service': service,
        'staff': staff,
        'start_datetime': start_datetime,
    }
    
    if request.method == 'POST':
        make_recurring = request.POST.get('make_recurring')
        if make_recurring:
            repeat_type = request.POST.get('repeat_type', 'weekly')
            repeat_interval = int(request.POST.get('repeat_interval', 1))
            until_date = request.POST.get('until_date', '')
            save_booking_data(request, {
                'repeat_type': repeat_type,
                'repeat_interval': repeat_interval,
                'until_date': until_date,
            })
        request.session[SESSION_KEY_BOOKING_STEP] = 4
        return redirect('appointments:booking_step5_cart')
    
    return render(request, 'appointments/booking_step4_repeat.html', context)


@login_required
def booking_step5_cart(request):
    """Step 5: Cart Review"""
    booking_data = get_booking_data(request)
    
    if 'start_datetime' not in booking_data:
        messages.error(request, 'Please start from the beginning.')
        return redirect('appointments:booking_step1_service')
    
    try:
        service = Service.objects.get(id=booking_data['service_id'])
        staff = Staff.objects.get(id=booking_data.get('staff_id'))
    except (Service.DoesNotExist, Staff.DoesNotExist):
        messages.error(request, 'Invalid booking data.')
        return redirect('appointments:booking_step1_service')
    
    # Calculate price
    number_of_persons = booking_data.get('number_of_persons', 1)
    extras = booking_data.get('extras', [])
    total_price = calculate_appointment_price(service, staff, number_of_persons, extras)
    
    # Parse datetime
    start_datetime_str = booking_data.get('start_datetime')
    if not start_datetime_str:
        messages.error(request, 'Booking start time is missing.')
        return redirect('appointments:booking_step1_service')
    
    try:
        if isinstance(start_datetime_str, str):
            try:
                start_datetime = datetime.fromisoformat(start_datetime_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                try:
                    start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%dT%H:%M:%S%z')
                except:
                    start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%dT%H:%M:%S')
        else:
            start_datetime = start_datetime_str
        
        if isinstance(start_datetime, datetime) and timezone.is_naive(start_datetime):
            start_datetime = timezone.make_aware(start_datetime)
    except Exception as e:
        messages.error(request, f'Invalid start datetime format in session: {str(e)}')
        return redirect('appointments:booking_step1_service')
    
    # Parse end datetime
    try:
        end_datetime_str = booking_data.get('end_datetime', '')
        if end_datetime_str:
            if isinstance(end_datetime_str, str):
                try:
                    end_datetime = datetime.fromisoformat(end_datetime_str.replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    try:
                        end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%dT%H:%M:%S%z')
                    except:
                        end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%dT%H:%M:%S')
                if isinstance(end_datetime, datetime) and timezone.is_naive(end_datetime):
                    end_datetime = timezone.make_aware(end_datetime)
            else:
                end_datetime = end_datetime_str
        else:
            end_datetime = start_datetime + timedelta(minutes=service.duration)
    except Exception as e:
        messages.error(request, f'Invalid end datetime format in session: {str(e)}')
        end_datetime = start_datetime + timedelta(minutes=service.duration)
    
    context = {
        'service': service,
        'staff': staff,
        'number_of_persons': number_of_persons,
        'start_datetime': start_datetime,
        'end_datetime': end_datetime,
        'total_price': total_price,
        'extras': extras,
    }
    
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code', '')
        if coupon_code:
            # TODO: Implement coupon validation
            pass
        
        request.session[SESSION_KEY_BOOKING_STEP] = 5
        return redirect('appointments:booking_step6_customer')
    
    return render(request, 'appointments/booking_step5_cart.html', context)


@login_required
def booking_step6_customer(request):
    """Step 6: Customer Details"""
    booking_data = get_booking_data(request)
    
    if 'start_datetime' not in booking_data:
        messages.error(request, 'Please start from the beginning.')
        return redirect('appointments:booking_step1_service')
    
    # Pre-fill for logged-in users
    initial_data = {}
    if request.user.is_authenticated:
        try:
            customer = request.user.customer_profile
            initial_data = {
                'name': customer.name or request.user.get_full_name() or request.user.username,
                'email': customer.email or request.user.email,
                'phone': customer.phone or request.user.phone or '',
                'address_line1': customer.address_line1 or '',
                'address_line2': customer.address_line2 or '',
                'town_city': customer.city or '',
                'postcode': customer.postcode or '',
            }
        except:
            # If no customer profile, use user data
            initial_data = {
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
                'phone': request.user.phone or '',
            }
    
    context = {
        'initial_data': initial_data,
        'user': request.user,
    }
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        address_line1 = request.POST.get('address_line1', '')
        address_line2 = request.POST.get('address_line2', '')
        town_city = request.POST.get('town_city', '')
        postcode = request.POST.get('postcode', '')
        
        if not name or not email:
            messages.error(request, 'Name and email are required.')
            return render(request, 'appointments/booking_step6_customer.html', context)
        
        if not address_line1 or not town_city or not postcode:
            messages.error(request, 'Address Line 1, Town/City, and Postcode are required.')
            return render(request, 'appointments/booking_step6_customer.html', context)
        
        save_booking_data(request, {
            'customer_name': name,
            'customer_email': email,
            'customer_phone': phone,
            'address_line1': address_line1,
            'address_line2': address_line2,
            'town_city': town_city,
            'postcode': postcode,
        })
        request.session[SESSION_KEY_BOOKING_STEP] = 6
        
        # Check if payment is needed
        try:
            service = Service.objects.get(id=booking_data['service_id'])
            staff = Staff.objects.get(id=booking_data.get('staff_id'))
            number_of_persons = booking_data.get('number_of_persons', 1)
            extras = booking_data.get('extras', [])
            total_price = calculate_appointment_price(service, staff, number_of_persons, extras)
            
            if total_price > 0:
                return redirect('appointments:booking_step7_payment')
            else:
                return redirect('appointments:booking_step8_confirmation')
        except:
            return redirect('appointments:booking_step7_payment')
    
    return render(request, 'appointments/booking_step6_customer.html', context)


@login_required
def booking_step7_payment(request):
    """Step 7: Payment"""
    booking_data = get_booking_data(request)
    
    if 'customer_email' not in booking_data:
        messages.error(request, 'Please start from the beginning.')
        return redirect('appointments:booking_step1_service')
    
    try:
        service = Service.objects.get(id=booking_data['service_id'])
    except Service.DoesNotExist:
        messages.error(request, 'Service not found.')
        return redirect('appointments:booking_step1_service')
    
    # Get staff
    staff_id = booking_data.get('staff_id')
    if staff_id:
        try:
            staff = Staff.objects.get(id=staff_id, is_active=True)
        except Staff.DoesNotExist:
            staff_list = get_staff_for_service(service)
            staff = staff_list[0] if staff_list else None
    else:
        staff_list = get_staff_for_service(service)
        staff = staff_list[0] if staff_list else None
    
    if not staff:
        messages.error(request, 'No staff available for this service.')
        return redirect('appointments:booking_step1_service')
    
    number_of_persons = booking_data.get('number_of_persons', 1)
    extras = booking_data.get('extras', [])
    total_price = calculate_appointment_price(service, staff, number_of_persons, extras)
    
    context = {
        'service': service,
        'staff': staff,
        'total_price': total_price,
        'STRIPE_PUBLISHABLE_KEY': getattr(settings, 'STRIPE_PUBLISHABLE_KEY', ''),
        'PAYPAL_CLIENT_ID': getattr(settings, 'PAYPAL_CLIENT_ID', ''),
    }
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'local')
        
        # For local payment, proceed directly to confirmation
        if payment_method == 'local':
            save_booking_data(request, {
                'payment_method': payment_method,
            })
            request.session[SESSION_KEY_BOOKING_STEP] = 7
            return redirect('appointments:booking_step8_confirmation')
        
        # For Stripe/PayPal, create payment intent/order
        from payments.services import get_payment_service
        from payments.models import Payment
        
        payment_service = get_payment_service(payment_method)
        customer_email = booking_data.get('customer_email', '')
        customer_name = booking_data.get('customer_name', '')
        description = f"{service.title} - {staff.full_name}"
        
        result = payment_service.create_payment(
            amount=total_price,
            customer_email=customer_email,
            customer_name=customer_name,
            description=description,
            metadata={
                'service_id': str(service.id),
                'staff_id': str(staff.id),
                'number_of_persons': str(number_of_persons),
            }
        )
        
        if result.get('success'):
            # Create payment record
            payment = Payment.objects.create(
                type=payment_method,
                status=Payment.STATUS_PENDING,
                total=total_price,
                paid=Decimal('0.00'),
                transaction_id=result.get('payment_id'),
                details={
                    'service_id': str(service.id),
                    'staff_id': str(staff.id),
                    'customer_email': customer_email,
                    'customer_name': customer_name,
                    'client_secret': result.get('client_secret'),
                }
            )
            
            save_booking_data(request, {
                'payment_method': payment_method,
                'payment_id': str(payment.id),
                'payment_client_secret': result.get('client_secret'),
            })
            request.session[SESSION_KEY_BOOKING_STEP] = 7
            
            # Redirect based on payment method
            if payment_method == 'stripe':
                context['payment'] = payment
                context['client_secret'] = result.get('client_secret')
                context['stripe_publishable_key'] = getattr(settings, 'STRIPE_PUBLISHABLE_KEY', '')
                return render(request, 'appointments/booking_step7_payment_stripe.html', context)
            elif payment_method == 'paypal':
                redirect_url = result.get('redirect_url')
                if redirect_url:
                    return redirect(redirect_url)
                else:
                    messages.error(request, 'Failed to create PayPal payment.')
        else:
            messages.error(request, f"Payment error: {result.get('error', 'Unknown error')}")
            return render(request, 'appointments/booking_step7_payment.html', context)
    
    return render(request, 'appointments/booking_step7_payment.html', context)


@login_required
def booking_step8_confirmation(request):
    """Step 8: Confirmation - Create Appointment"""
    booking_data = get_booking_data(request)
    
    if 'customer_email' not in booking_data or 'start_datetime' not in booking_data:
        messages.error(request, 'Please start from the beginning.')
        return redirect('appointments:booking_step1_service')
    
    try:
        service = Service.objects.get(id=booking_data['service_id'])
    except Service.DoesNotExist:
        messages.error(request, 'Service not found.')
        return redirect('appointments:booking_step1_service')
    
    # Get staff
    staff_id = booking_data.get('staff_id')
    if staff_id:
        try:
            staff = Staff.objects.get(id=staff_id, is_active=True)
        except Staff.DoesNotExist:
            staff_list = get_staff_for_service(service)
            staff = staff_list[0] if staff_list else None
    else:
        staff_list = get_staff_for_service(service)
        staff = staff_list[0] if staff_list else None
    
    if not staff:
        messages.error(request, 'No staff available for this service.')
        return redirect('appointments:booking_step1_service')
    
    # Create or get customer
    customer_email = booking_data['customer_email']
    customer, created = Customer.objects.get_or_create(
        email=customer_email,
        defaults={
            'name': booking_data['customer_name'],
            'phone': booking_data.get('customer_phone', ''),
            'address_line1': booking_data.get('address_line1', ''),
            'address_line2': booking_data.get('address_line2', ''),
            'city': booking_data.get('town_city', '') or booking_data.get('city', ''),
            'postcode': booking_data.get('postcode', ''),
        }
    )
    
    # Link to user if logged in
    if request.user.is_authenticated and not customer.user:
        customer.user = request.user
        customer.save()
    
    # Parse datetime
    start_datetime_str = booking_data.get('start_datetime')
    if not start_datetime_str:
        messages.error(request, 'Please start from the beginning.')
        return redirect('appointments:booking_step1_service')
    
    try:
        if isinstance(start_datetime_str, str):
            try:
                start_datetime = datetime.fromisoformat(start_datetime_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                try:
                    start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%dT%H:%M:%S%z')
                except:
                    start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%dT%H:%M:%S')
        else:
            start_datetime = start_datetime_str
        
        if isinstance(start_datetime, datetime) and timezone.is_naive(start_datetime):
            start_datetime = timezone.make_aware(start_datetime)
    except Exception as e:
        messages.error(request, f'Invalid datetime format: {str(e)}')
        return redirect('appointments:booking_step1_service')
    
    # Parse end datetime
    try:
        end_datetime_str = booking_data.get('end_datetime', '')
        if end_datetime_str:
            try:
                if isinstance(end_datetime_str, str):
                    try:
                        end_datetime = datetime.fromisoformat(end_datetime_str.replace('Z', '+00:00'))
                    except (ValueError, AttributeError):
                        try:
                            end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%dT%H:%M:%S%z')
                        except:
                            end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%dT%H:%M:%S')
                    if isinstance(end_datetime, datetime) and timezone.is_naive(end_datetime):
                        end_datetime = timezone.make_aware(end_datetime)
                else:
                    end_datetime = end_datetime_str
            except:
                end_datetime = start_datetime + timedelta(minutes=service.duration)
        else:
            end_datetime = start_datetime + timedelta(minutes=service.duration)
    except:
        end_datetime = start_datetime + timedelta(minutes=service.duration)
    
    appointment = Appointment.objects.create(
        staff=staff,
        service=service,
        start_date=start_datetime,
        end_date=end_datetime,
        extras_duration=0,
    )
    
    # Create payment record if not already created
    payment = None
    payment_method = booking_data.get('payment_method', 'local')
    payment_id = booking_data.get('payment_id')
    
    if payment_id:
        try:
            from payments.models import Payment
            payment = Payment.objects.get(id=payment_id)
        except:
            pass
    elif payment_method == 'local':
        from payments.models import Payment
        number_of_persons = booking_data.get('number_of_persons', 1)
        extras = booking_data.get('extras', [])
        total_price = calculate_appointment_price(service, staff, number_of_persons, extras)
        
        payment = Payment.objects.create(
            type=Payment.TYPE_LOCAL,
            status=Payment.STATUS_PENDING,
            total=total_price,
            paid=Decimal('0.00'),
            details={
                'service_id': str(service.id),
                'staff_id': str(staff.id),
                'customer_email': customer_email,
                'customer_name': booking_data.get('customer_name', ''),
            }
        )
    
    # Create customer appointment
    from payments.models import Payment as PaymentModel
    customer_appointment = CustomerAppointment.objects.create(
        customer=customer,
        appointment=appointment,
        number_of_persons=booking_data.get('number_of_persons', 1),
        extras=booking_data.get('extras', []),
        custom_fields=booking_data.get('custom_fields', []),
        status=CustomerAppointment.STATUS_PENDING if (payment and payment.status == PaymentModel.STATUS_PENDING) else CustomerAppointment.STATUS_APPROVED,
        payment=payment,
        time_zone_offset=booking_data.get('time_zone_offset', 0),
    )
    
    # Send confirmation notifications (signals will handle this automatically)
    # Note: Notifications are sent via Django signals in notifications/signals.py
    
    # Sync with calendar (Google/Outlook/Apple)
    if staff.calendar_provider != 'none':
        from calendar_sync.services import get_calendar_service
        calendar_service = get_calendar_service(staff)
        if calendar_service:
            try:
                result = calendar_service.create_event(appointment, customer_appointment, request)
                if result.get('success'):
                    appointment.calendar_event_id = result.get('event_id', '')
                    appointment.calendar_provider = staff.calendar_provider
                    appointment.save()
                else:
                    logger.warning(f"Calendar sync failed: {result.get('error')}")
            except Exception as e:
                logger.error(f"Error syncing calendar: {str(e)}")
    
    # Get QR code and links
    from core.utils import generate_appointment_qr_code, get_appointment_links
    try:
        qr_code_buffer = generate_appointment_qr_code(appointment, customer_appointment, request)
        qr_code_base64 = base64.b64encode(qr_code_buffer.getvalue()).decode('utf-8')
    except Exception as e:
        logger.error(f"Error generating QR code: {str(e)}")
        qr_code_base64 = None
    
    appointment_links = get_appointment_links(appointment, customer_appointment, request)
    
    context = {
        'appointment': appointment,
        'customer_appointment': customer_appointment,
        'customer': customer,
        'qr_code': qr_code_base64,
        'appointment_links': appointment_links,
    }
    
    # Clear booking session
    clear_booking_session(request)
    
    messages.success(request, 'Your appointment has been booked successfully!')
    
    return render(request, 'appointments/booking_step8_confirmation.html', context)


@login_required
def calendar_view(request):
    """Calendar view for appointments."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    try:
        year = int(request.GET.get('year', timezone.now().year))
        month = int(request.GET.get('month', timezone.now().month))
    except (ValueError, TypeError):
        year = timezone.now().year
        month = timezone.now().month
    
    if month < 1 or month > 12:
        month = timezone.now().month
    if year < 2000 or year > 2100:
        year = timezone.now().year
    
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
    
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    
    first_day = date(year, month, 1)
    last_day_num = calendar.monthrange(year, month)[1]
    last_day = date(year, month, last_day_num)
    
    month_start = timezone.make_aware(datetime.combine(first_day, datetime.min.time()))
    month_end = timezone.make_aware(datetime.combine(last_day, datetime.max.time()))
    
    appointments = Appointment.objects.none()
    filter_staff = None
    filter_customer = None
    
    if request.user.is_superuser or request.user.role == User.ROLE_ADMIN:
        appointments = Appointment.objects.filter(
            start_date__gte=month_start,
            start_date__lte=month_end
        ).select_related('staff', 'service').prefetch_related('customer_appointments__customer')
        
        staff_id = request.GET.get('staff_id')
        if staff_id:
            try:
                filter_staff = Staff.objects.get(id=staff_id)
                appointments = appointments.filter(staff=filter_staff)
            except Staff.DoesNotExist:
                pass
        
        customer_id = request.GET.get('customer_id')
        if customer_id:
            try:
                filter_customer = Customer.objects.get(id=customer_id)
                appointments = appointments.filter(customer_appointments__customer=filter_customer).distinct()
            except Customer.DoesNotExist:
                pass
        
        all_staff = Staff.objects.filter(is_active=True).order_by('full_name')
        all_customers = Customer.objects.all().order_by('name')
    
    elif request.user.role == User.ROLE_STAFF:
        try:
            staff_profile = Staff.objects.get(user=request.user)
            appointments = Appointment.objects.filter(
                staff=staff_profile,
                start_date__gte=month_start,
                start_date__lte=month_end
            ).select_related('service').prefetch_related('customer_appointments__customer')
            filter_staff = staff_profile
        except Staff.DoesNotExist:
            messages.warning(request, "Your staff profile is not set up.")
    
    elif request.user.role == User.ROLE_CUSTOMER:
        try:
            customer_profile = Customer.objects.get(user=request.user)
            appointments = CustomerAppointment.objects.filter(
                customer=customer_profile,
                appointment__start_date__gte=month_start,
                appointment__start_date__lte=month_end
            ).select_related('appointment__staff', 'appointment__service').order_by('appointment__start_date')
            filter_customer = customer_profile
        except Customer.DoesNotExist:
            messages.warning(request, "Your customer profile is not set up.")
    
    appointments_by_date = {}
    for appt in appointments:
        if request.user.role == User.ROLE_CUSTOMER:
            appt_date = appt.appointment.start_date.date()
            if appt_date not in appointments_by_date:
                appointments_by_date[appt_date] = []
            appointments_by_date[appt_date].append(appt.appointment)
        else:
            appt_date = appt.start_date.date()
            if appt_date not in appointments_by_date:
                appointments_by_date[appt_date] = []
            appointments_by_date[appt_date].append(appt)
    
    cal = calendar.Calendar()
    month_calendar = cal.monthdayscalendar(year, month)
    
    context = {
        'year': year,
        'month': month,
        'month_name': date(year, month, 1).strftime('%B'),
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'today': timezone.now().date(),
        'calendar': month_calendar,
        'appointments_by_date': appointments_by_date,
        'filter_staff': filter_staff,
        'filter_customer': filter_customer,
        'all_staff': all_staff if request.user.is_superuser or request.user.role == User.ROLE_ADMIN else [],
        'all_customers': all_customers if request.user.is_superuser or request.user.role == User.ROLE_ADMIN else [],
    }
    
    return render(request, 'appointments/calendar.html', context)


def view_appointment_by_token(request, token):
    """View appointment details using token (public access)."""
    customer_appointment = get_object_or_404(CustomerAppointment, token=token)
    appointment = customer_appointment.appointment
    
    context = {
        'appointment': appointment,
        'customer_appointment': customer_appointment,
        'customer': customer_appointment.customer,
    }
    
    return render(request, 'appointments/view_appointment.html', context)


@require_http_methods(["GET", "POST"])
def cancel_appointment_by_token(request, token):
    """Cancel appointment using token (public access)."""
    customer_appointment = get_object_or_404(CustomerAppointment, token=token)
    appointment = customer_appointment.appointment
    
    if request.method == 'POST':
        # Delete the CustomerAppointment (this removes it from all dashboards)
        # If this is the only CustomerAppointment for the Appointment, delete the Appointment too
        appointment_id = appointment.id
        other_customer_appointments = CustomerAppointment.objects.filter(
            appointment=appointment
        ).exclude(id=customer_appointment.id)
        
        # Delete the CustomerAppointment
        customer_appointment.delete()
        
        # If no other CustomerAppointments exist for this Appointment, delete the Appointment too
        if not other_customer_appointments.exists():
            appointment.delete()
            messages.success(request, 'Your appointment has been cancelled and deleted successfully.')
        else:
            messages.success(request, 'Your appointment has been cancelled successfully.')
        
        # Redirect to home or customer dashboard if logged in
        if request.user.is_authenticated:
            try:
                from customers.models import Customer
                customer = Customer.objects.get(user=request.user)
                return redirect('customers:customer_dashboard')
            except Customer.DoesNotExist:
                pass
        
        return redirect('home')
    
    context = {
        'customer_appointment': customer_appointment,
        'appointment': appointment,
    }
    
    return render(request, 'appointments/cancel_appointment.html', context)
