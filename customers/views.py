"""
Views for customers app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Customer
from .forms import CustomerForm


def is_admin_or_staff(user):
    """Check if user is admin or staff."""
    return user.is_authenticated and (user.is_superuser or user.role in ['admin', 'staff'])


def can_edit_customer(user, customer):
    """Check if user can edit this customer."""
    # Admin/Staff can edit any customer
    if is_admin_or_staff(user):
        return True
    # Customer can only edit their own profile
    if user.role == 'customer' and customer.user == user:
        return True
    return False


@login_required
def customer_dashboard(request):
    """Customer dashboard view."""
    from appointments.models import CustomerAppointment, Appointment
    
    # Get or create customer profile for current user
    customer, created = Customer.objects.get_or_create(
        user=request.user,
        defaults={
            'name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
        }
    )
    
    if created:
        messages.info(request, 'Welcome! Please complete your profile.')
    
    # Get upcoming appointments (all statuses except cancelled)
    now = timezone.now()
    upcoming_appointments = CustomerAppointment.objects.filter(
        customer=customer,
        appointment__start_date__gte=now
    ).exclude(status='cancelled').select_related('appointment', 'appointment__service', 'appointment__staff').order_by('appointment__start_date')[:10]
    
    # Get past appointments
    past_appointments = CustomerAppointment.objects.filter(
        customer=customer,
        appointment__start_date__lt=now
    ).select_related('appointment', 'appointment__service', 'appointment__staff').order_by('-appointment__start_date')[:5]
    
    context = {
        'customer': customer,
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
    }
    
    return render(request, 'customers/customer_dashboard.html', context)


@login_required
def customer_edit(request, pk):
    """Edit a customer - accessible by admin/staff or the customer themselves."""
    customer = get_object_or_404(Customer, pk=pk)
    
    # Check permissions
    if not can_edit_customer(request.user, customer):
        messages.error(request, 'You do not have permission to edit this customer profile.')
        return redirect('profile')
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save()
            messages.success(request, 'Customer profile updated successfully.')
            # Redirect based on user role
            if request.user.role == 'customer':
                return redirect('profile')
            return redirect('customers:customer_list')
    else:
        form = CustomerForm(instance=customer)
    
    return render(request, 'customers/customer_form.html', {
        'form': form,
        'customer': customer,
        'title': 'Edit Customer Profile'
    })


@login_required
@user_passes_test(is_admin_or_staff)
def customer_list(request):
    """List all customers."""
    search_query = request.GET.get('search', '')
    
    customers = Customer.objects.all()
    
    if search_query:
        customers = customers.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(postcode__icontains=search_query)
        )
    
    customers = customers.order_by('name')
    
    # Pagination
    paginator = Paginator(customers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'customers/customer_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
    })


@login_required
@user_passes_test(is_admin_or_staff)
def customer_create(request):
    """Create a new customer."""
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, f'Customer "{customer.name}" created successfully.')
            return redirect('customers:customer_list')
    else:
        form = CustomerForm()
    return render(request, 'customers/customer_form.html', {'form': form, 'title': 'Create Customer'})


@login_required
@user_passes_test(is_admin_or_staff)
def customer_delete(request, pk):
    """Delete a customer."""
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, f'Customer "{customer.name}" deleted successfully.')
        return redirect('customers:customer_list')
    return render(request, 'customers/customer_confirm_delete.html', {'customer': customer})


@login_required
@user_passes_test(is_admin_or_staff)
def customer_detail(request, pk):
    """View customer details."""
    customer = get_object_or_404(Customer, pk=pk)
    appointments = customer.customer_appointments.all().select_related(
        'appointment', 'appointment__service', 'appointment__staff'
    ).order_by('-appointment__start_date')[:10]
    
    return render(request, 'customers/customer_detail.html', {
        'customer': customer,
        'appointments': appointments,
    })
