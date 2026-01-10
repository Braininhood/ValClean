"""
Accounts app models.
User, Profile, and Manager models.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Supports roles: admin, manager, staff, customer
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
        ('customer', 'Customer'),
    ]
    
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='customer',
        help_text='User role: admin, manager, staff, or customer'
    )
    is_verified = models.BooleanField(
        default=False,
        help_text='Email verification status'
    )
    
    # Override username to be optional (use email as primary identifier)
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        null=True,
        blank=True,
        help_text='Optional username. Email is used as primary identifier.'
    )
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'accounts_user'
        
    def __str__(self):
        return self.email or self.username or f"User {self.id}"
    
    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser
    
    @property
    def is_manager(self):
        return self.role == 'manager'
    
    @property
    def is_staff_member(self):
        return self.role == 'staff'
    
    @property
    def is_customer(self):
        return self.role == 'customer'


class Profile(TimeStampedModel):
    """
    User profile with calendar sync capabilities.
    All roles (admin, manager, staff, customer) can sync calendars.
    """
    CALENDAR_PROVIDER_CHOICES = [
        ('none', 'None'),
        ('google', 'Google Calendar'),
        ('outlook', 'Microsoft Outlook'),
        ('apple', 'Apple Calendar'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        help_text='Associated user'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text='Phone number (UK format)'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text='User avatar image'
    )
    timezone = models.CharField(
        max_length=50,
        default='Europe/London',
        help_text='User timezone (e.g., Europe/London)'
    )
    preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text='User preferences (JSON)'
    )
    
    # Calendar Sync Fields (for all roles)
    calendar_sync_enabled = models.BooleanField(
        default=False,
        help_text='Enable calendar synchronization'
    )
    calendar_provider = models.CharField(
        max_length=20,
        choices=CALENDAR_PROVIDER_CHOICES,
        default='none',
        help_text='Calendar provider: google, outlook, apple, or none'
    )
    calendar_access_token = models.TextField(
        blank=True,
        null=True,
        help_text='Encrypted calendar access token'
    )
    calendar_refresh_token = models.TextField(
        blank=True,
        null=True,
        help_text='Encrypted calendar refresh token'
    )
    calendar_calendar_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Calendar ID from provider (e.g., Google Calendar ID)'
    )
    calendar_sync_settings = models.JSONField(
        default=dict,
        blank=True,
        help_text='Calendar sync preferences (JSON): auto_sync, sync_direction, etc.'
    )
    
    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')
        db_table = 'accounts_profile'
    
    def __str__(self):
        return f"{self.user.email}'s Profile"


class Manager(TimeStampedModel):
    """
    Manager model with flexible permissions configuration.
    Permissions are assigned by admin and can be location-based, staff-based, or customer-based.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='manager_profile',
        limit_choices_to={'role': 'manager'},
        help_text='Manager user (must have role=manager)'
    )
    permissions = models.JSONField(
        default=dict,
        blank=True,
        help_text='Permission configuration (JSON): can_manage_customers, can_manage_staff, etc.'
    )
    can_manage_all = models.BooleanField(
        default=False,
        help_text='Can manage all staff and customers (full manager access)'
    )
    can_manage_customers = models.BooleanField(
        default=False,
        help_text='Can manage customers (within assigned scope)'
    )
    can_manage_staff = models.BooleanField(
        default=False,
        help_text='Can manage staff (within assigned scope)'
    )
    can_manage_appointments = models.BooleanField(
        default=True,
        help_text='Can manage appointments (within assigned scope)'
    )
    can_view_reports = models.BooleanField(
        default=True,
        help_text='Can view reports (within assigned scope)'
    )
    
    # Location-based permissions (optional - for future multi-location support)
    managed_locations = models.JSONField(
        default=list,
        blank=True,
        help_text='List of location IDs this manager can manage (JSON array)'
    )
    
    # Staff-based permissions
    managed_staff = models.ManyToManyField(
        'staff.Staff',
        related_name='managing_managers',
        blank=True,
        help_text='Staff members this manager can manage'
    )
    
    # Customer-based permissions
    managed_customers = models.ManyToManyField(
        'customers.Customer',
        related_name='managing_managers',
        blank=True,
        help_text='Customers this manager can manage'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Manager account is active'
    )
    
    class Meta:
        verbose_name = _('manager')
        verbose_name_plural = _('managers')
        db_table = 'accounts_manager'
    
    def __str__(self):
        return f"Manager: {self.user.email}"
    
    def save(self, *args, **kwargs):
        # Ensure user role is 'manager'
        if self.user.role != 'manager':
            self.user.role = 'manager'
            self.user.save()
        super().save(*args, **kwargs)
