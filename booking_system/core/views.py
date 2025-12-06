"""
Core views for the booking system.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.utils import get_redirect_url_for_user


def home(request):
    """Home page view."""
    if request.user.is_authenticated:
        return redirect(get_redirect_url_for_user(request.user))
    return redirect('login')


@login_required
def dashboard(request):
    """General dashboard view - redirects to role-specific dashboard."""
    return redirect(get_redirect_url_for_user(request.user))
