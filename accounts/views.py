"""
Authentication views.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from .forms import LoginForm, RegistrationForm, ProfileEditForm
from .utils import get_redirect_url_for_user

User = get_user_model()


@require_http_methods(["GET", "POST"])
def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect(get_redirect_url_for_user(request.user))
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                next_url = request.GET.get('next', None)
                if next_url:
                    return redirect(next_url)
                return redirect(get_redirect_url_for_user(user))
            else:
                # Check if user exists with this username
                if User.objects.filter(username=username).exists():
                    messages.error(request, 'Invalid password. Please try again.')
                else:
                    messages.warning(request, 'Username not found. Would you like to register?')
                    return redirect('register')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@require_http_methods(["GET", "POST"])
def register_view(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect(get_redirect_url_for_user(request.user))
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                messages.warning(request, 'Username already exists. Please login instead.')
                return redirect('login')
            
            if User.objects.filter(email=email).exists():
                messages.warning(request, 'Email already registered. Please login instead.')
                return redirect('login')
            
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            
            # Redirect based on user role
            return redirect(get_redirect_url_for_user(user))
    else:
        form = RegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
@require_http_methods(["GET", "POST"])
def profile_view(request):
    """User profile view with edit functionality."""
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=request.user)
    
    # Get staff profile if user is staff
    staff_profile = None
    if request.user.role == 'staff':
        try:
            from staff.models import Staff
            staff_profile = Staff.objects.filter(user=request.user).first()
        except:
            pass
    
    # Get customer profile if user is customer
    customer_profile = None
    if request.user.role == 'customer':
        try:
            from customers.models import Customer
            customer_profile = Customer.objects.filter(user=request.user).first()
        except:
            pass
    
    return render(request, 'accounts/profile.html', {
        'form': form,
        'user': request.user,
        'staff_profile': staff_profile,
        'customer_profile': customer_profile,
    })


@require_http_methods(["GET", "POST"])
def logout_view(request):
    """User logout view that accepts both GET and POST."""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')
