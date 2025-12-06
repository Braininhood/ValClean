"""
Views for services app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Category, Service
from .forms import CategoryForm, ServiceForm


def is_admin_or_staff(user):
    """Check if user is admin or staff."""
    return user.is_authenticated and (user.is_superuser or user.role in ['admin', 'staff'])


@login_required
@user_passes_test(is_admin_or_staff)
def category_list(request):
    """List all categories."""
    categories = Category.objects.filter(is_active=True).order_by('position', 'name')
    return render(request, 'services/category_list.html', {'categories': categories})


@login_required
@user_passes_test(is_admin_or_staff)
def category_create(request):
    """Create a new category."""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" created successfully.')
            return redirect('services:category_list')
    else:
        form = CategoryForm()
    return render(request, 'services/category_form.html', {'form': form, 'title': 'Create Category'})


@login_required
@user_passes_test(is_admin_or_staff)
def category_edit(request, pk):
    """Edit a category."""
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" updated successfully.')
            return redirect('services:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'services/category_form.html', {
        'form': form,
        'category': category,
        'title': 'Edit Category'
    })


@login_required
@user_passes_test(is_admin_or_staff)
def category_delete(request, pk):
    """Delete a category."""
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.is_active = False
        category.save()
        messages.success(request, f'Category "{category.name}" deleted successfully.')
        return redirect('services:category_list')
    return render(request, 'services/category_confirm_delete.html', {'category': category})


@login_required
@user_passes_test(is_admin_or_staff)
def service_list(request):
    """List all services."""
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    
    services = Service.objects.filter(is_active=True)
    
    if search_query:
        services = services.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if category_filter:
        services = services.filter(category_id=category_filter)
    
    services = services.order_by('position', 'title')
    
    # Pagination
    paginator = Paginator(services, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.filter(is_active=True)
    
    return render(request, 'services/service_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
    })


@login_required
@user_passes_test(is_admin_or_staff)
def service_create(request):
    """Create a new service."""
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save()
            messages.success(request, f'Service "{service.title}" created successfully.')
            return redirect('services:service_list')
    else:
        form = ServiceForm()
    return render(request, 'services/service_form.html', {'form': form, 'title': 'Create Service'})


@login_required
@user_passes_test(is_admin_or_staff)
def service_edit(request, pk):
    """Edit a service."""
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            service = form.save()
            messages.success(request, f'Service "{service.title}" updated successfully.')
            return redirect('services:service_list')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'services/service_form.html', {
        'form': form,
        'service': service,
        'title': 'Edit Service'
    })


@login_required
@user_passes_test(is_admin_or_staff)
def service_delete(request, pk):
    """Delete a service."""
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.is_active = False
        service.save()
        messages.success(request, f'Service "{service.title}" deleted successfully.')
        return redirect('services:service_list')
    return render(request, 'services/service_confirm_delete.html', {'service': service})


@login_required
def service_detail(request, pk):
    """View service details."""
    service = get_object_or_404(Service, pk=pk, is_active=True)
    return render(request, 'services/service_detail.html', {'service': service})
