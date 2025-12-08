"""
Views for staff app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
import logging
from .models import Staff, StaffScheduleItem, StaffService, Holiday
from .forms import StaffForm, StaffScheduleItemForm, StaffServiceForm, HolidayForm

logger = logging.getLogger(__name__)


def is_admin(user):
    """Check if user is admin."""
    return user.is_authenticated and (user.is_superuser or user.role == 'admin')


def can_edit_staff(user, staff):
    """Check if user can edit this staff profile."""
    # Admin can edit any staff
    if is_admin(user):
        return True
    # Staff can only edit their own profile
    if user.role == 'staff' and staff.user == user:
        return True
    return False


def is_staff_or_admin(user):
    """Check if user is staff or admin."""
    return user.is_authenticated and (user.is_superuser or user.role in ['admin', 'staff'])


@login_required
@user_passes_test(is_staff_or_admin)
def staff_dashboard(request):
    """Staff dashboard view."""
    from appointments.models import Appointment, CustomerAppointment
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    # Get staff member for current user
    try:
        staff = Staff.objects.get(user=request.user)
    except Staff.DoesNotExist:
        # If staff profile doesn't exist, redirect to profile completion
        messages.warning(request, 'Please complete your staff profile to continue.')
        return redirect('staff:staff_complete_profile')
    
    # Get upcoming appointments for this staff member (with customer info)
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    # Get appointments with customer information
    upcoming_appointments = Appointment.objects.filter(
        staff=staff,
        start_date__gte=now
    ).select_related('service').prefetch_related('customer_appointments__customer').order_by('start_date')[:20]
    
    today_appointments = Appointment.objects.filter(
        staff=staff,
        start_date__gte=today_start,
        start_date__lt=today_end
    ).select_related('service').prefetch_related('customer_appointments__customer').order_by('start_date')
    
    total_appointments = Appointment.objects.filter(staff=staff).count()
    
    context = {
        'staff': staff,
        'upcoming_appointments': upcoming_appointments,
        'today_appointments': today_appointments,
        'total_appointments': total_appointments,
    }
    
    return render(request, 'staff/staff_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def staff_list(request):
    """List all staff members."""
    search_query = request.GET.get('search', '')
    
    staff_members = Staff.objects.filter(is_active=True)
    
    if search_query:
        staff_members = staff_members.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    staff_members = staff_members.order_by('position', 'full_name')
    
    # Pagination
    paginator = Paginator(staff_members, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'staff/staff_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
    })


@login_required
@user_passes_test(is_admin)
def staff_create(request):
    """Create a new staff member."""
    if request.method == 'POST':
        form = StaffForm(request.POST, request.FILES)
        if form.is_valid():
            staff = form.save()
            messages.success(request, f'Staff member "{staff.full_name}" created successfully.')
            return redirect('staff:staff_list')
    else:
        form = StaffForm()
    return render(request, 'staff/staff_form.html', {'form': form, 'title': 'Create Staff Member'})


@login_required
def staff_complete_profile(request):
    """Allow staff to complete their profile after registration."""
    # Check if user is staff
    if request.user.role != 'staff':
        messages.error(request, 'This page is only for staff members.')
        return redirect('home')
    
    # Check if profile already exists
    try:
        staff = Staff.objects.get(user=request.user)
        messages.info(request, 'Your staff profile already exists. You can edit it below.')
        return redirect('staff:staff_edit', pk=staff.pk)
    except Staff.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = StaffForm(request.POST, request.FILES, is_completion=True)
        if form.is_valid():
            staff = form.save(commit=False)
            # Automatically link to current user
            staff.user = request.user
            # Set default values if not provided
            if not staff.email:
                staff.email = request.user.email
            if not staff.full_name:
                staff.full_name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
            staff.is_active = True
            staff.visibility = 'public'
            staff.save()
            messages.success(request, 'Staff profile created successfully! You can now manage your schedule and services.')
            return redirect('staff:staff_dashboard')
        else:
            # Show form errors
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-fill form with user data
        initial_data = {
            'email': request.user.email,
            'full_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            'phone': getattr(request.user, 'phone', '') if hasattr(request.user, 'phone') else '',
        }
        form = StaffForm(initial=initial_data, is_completion=True)
    
    return render(request, 'staff/staff_form.html', {
        'form': form,
        'title': 'Complete Your Staff Profile',
        'is_completion': True,
    })


@login_required
def staff_edit(request, pk):
    """Edit a staff member - accessible by admin or the staff member themselves."""
    staff = get_object_or_404(Staff, pk=pk)
    
    # Check permissions
    if not can_edit_staff(request.user, staff):
        messages.error(request, 'You do not have permission to edit this staff profile.')
        if request.user.role == 'staff':
            return redirect('profile')
        return redirect('staff:staff_list')
    
    if request.method == 'POST':
        form = StaffForm(request.POST, request.FILES, instance=staff)
        if form.is_valid():
            staff = form.save()
            messages.success(request, f'Staff profile updated successfully.')
            # Redirect based on user role
            if request.user.role == 'staff':
                return redirect('staff:staff_dashboard')
            return redirect('staff:staff_list')
    else:
        form = StaffForm(instance=staff)
    
    # Determine title based on who's editing
    if request.user.role == 'staff':
        title = 'Edit My Staff Profile'
    else:
        title = 'Edit Staff Member'
    
    return render(request, 'staff/staff_form.html', {
        'form': form,
        'staff': staff,
        'title': title
    })


@login_required
@user_passes_test(is_admin)
def staff_delete(request, pk):
    """Delete a staff member."""
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == 'POST':
        staff.is_active = False
        staff.save()
        messages.success(request, f'Staff member "{staff.full_name}" deleted successfully.')
        return redirect('staff:staff_list')
    return render(request, 'staff/staff_confirm_delete.html', {'staff': staff})


@login_required
@user_passes_test(is_admin)
def staff_detail(request, pk):
    """View staff member details."""
    staff = get_object_or_404(Staff, pk=pk)
    schedule_items = staff.schedule_items.all().order_by('day_index')
    staff_services = staff.staff_services.all().select_related('service')
    holidays = staff.holidays.all().order_by('date')
    
    return render(request, 'staff/staff_detail.html', {
        'staff': staff,
        'schedule_items': schedule_items,
        'staff_services': staff_services,
        'holidays': holidays,
    })


@login_required
def staff_schedule_edit(request, staff_pk):
    """Edit staff schedule - accessible by admin or the staff member themselves."""
    staff = get_object_or_404(Staff, pk=staff_pk)
    
    # Check permissions - staff can only edit their own schedule
    if not can_edit_staff(request.user, staff):
        messages.error(request, 'You do not have permission to edit this schedule.')
        if request.user.role == 'staff':
            return redirect('staff:staff_dashboard')
        return redirect('staff:staff_list')
    
    if request.method == 'POST':
        # Handle schedule items
        day_indexes = request.POST.getlist('day_index')
        start_times = request.POST.getlist('start_time')
        end_times = request.POST.getlist('end_time')
        
        # Delete existing schedule items
        StaffScheduleItem.objects.filter(staff=staff).delete()
        
        # Create new schedule items
        for day_index, start_time, end_time in zip(day_indexes, start_times, end_times):
            if day_index and start_time and end_time:
                StaffScheduleItem.objects.create(
                    staff=staff,
                    day_index=int(day_index),
                    start_time=start_time,
                    end_time=end_time
                )
        
        messages.success(request, 'Schedule updated successfully.')
        # Redirect based on user role
        if request.user.role == 'staff':
            return redirect('staff:staff_dashboard')
        return redirect('staff:staff_detail', pk=staff_pk)
    
    schedule_items = staff.schedule_items.all().order_by('day_index')
    return render(request, 'staff/staff_schedule_edit.html', {
        'staff': staff,
        'schedule_items': schedule_items,
        'is_own_schedule': request.user.role == 'staff' and staff.user == request.user,
    })


@login_required
def staff_my_schedule(request):
    """Staff can edit their own schedule directly from dashboard."""
    if request.user.role != 'staff':
        messages.error(request, 'This page is only for staff members.')
        return redirect('home')
    
    try:
        staff = Staff.objects.get(user=request.user)
    except Staff.DoesNotExist:
        messages.warning(request, 'Please complete your staff profile first.')
        return redirect('staff:staff_complete_profile')
    
    return redirect('staff:staff_schedule_edit', staff_pk=staff.pk)


@login_required
def staff_my_services(request):
    """Staff can manage their assigned services."""
    if request.user.role != 'staff':
        messages.error(request, 'This page is only for staff members.')
        return redirect('home')
    
    try:
        staff = Staff.objects.get(user=request.user)
    except Staff.DoesNotExist:
        messages.warning(request, 'Please complete your staff profile first.')
        return redirect('staff:staff_complete_profile')
    
    from services.models import Service
    
    # Get all active public services
    all_services = Service.objects.filter(is_active=True, visibility='public').order_by('category', 'title')
    
    # Get currently assigned services
    assigned_services = staff.staff_services.all().select_related('service')
    assigned_service_ids = [ss.service.id for ss in assigned_services]
    
    if request.method == 'POST':
        # Handle service assignment/removal
        action = request.POST.get('action')
        service_id = request.POST.get('service_id')
        
        if action == 'add' and service_id:
            try:
                service = Service.objects.get(id=service_id, is_active=True)
                # Check if already assigned
                if not StaffService.objects.filter(staff=staff, service=service).exists():
                    StaffService.objects.create(
                        staff=staff,
                        service=service,
                        price=service.price,  # Use service default price
                        capacity=service.capacity,  # Use service default capacity
                    )
                    messages.success(request, f'Service "{service.title}" added successfully.')
                else:
                    messages.info(request, f'Service "{service.title}" is already assigned.')
            except Service.DoesNotExist:
                messages.error(request, 'Invalid service selected.')
        
        elif action == 'remove' and service_id:
            try:
                staff_service = StaffService.objects.get(staff=staff, service_id=service_id)
                service_title = staff_service.service.title
                staff_service.delete()
                messages.success(request, f'Service "{service_title}" removed successfully.')
            except StaffService.DoesNotExist:
                messages.error(request, 'Service not found.')
        
        elif action == 'update' and service_id:
            # Update price/capacity for assigned service
            try:
                staff_service = StaffService.objects.get(staff=staff, service_id=service_id)
                price = request.POST.get('price')
                capacity = request.POST.get('capacity')
                
                if price:
                    staff_service.price = price
                if capacity:
                    staff_service.capacity = int(capacity)
                staff_service.save()
                messages.success(request, f'Service "{staff_service.service.title}" updated successfully.')
            except (StaffService.DoesNotExist, ValueError):
                messages.error(request, 'Invalid update data.')
        
        return redirect('staff:staff_my_services')
    
    return render(request, 'staff/staff_my_services.html', {
        'staff': staff,
        'all_services': all_services,
        'assigned_services': assigned_services,
        'assigned_service_ids': assigned_service_ids,
    })
