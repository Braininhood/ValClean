"""
Custom permissions for role-based access control.
"""
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Permission check for Admin users.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'role') and
            request.user.role == 'admin'
        )


class IsManager(permissions.BasePermission):
    """
    Permission check for Manager users.
    Managers have flexible permissions assigned by admin.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'role') and
            request.user.role == 'manager'
        )


class IsStaff(permissions.BasePermission):
    """
    Permission check for Staff users.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'role') and
            request.user.role == 'staff'
        )


class IsCustomer(permissions.BasePermission):
    """
    Permission check for Customer users.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'role') and
            request.user.role == 'customer'
        )


class IsAdminOrManager(permissions.BasePermission):
    """
    Permission check for Admin or Manager users.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'role') and
            request.user.role in ['admin', 'manager']
        )


class IsStaffOrManager(permissions.BasePermission):
    """
    Permission check for Staff or Manager users.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'role') and
            request.user.role in ['staff', 'manager']
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission check for object owners or Admin users.
    """
    def has_object_permission(self, request, view, obj):
        # Admin can access anything
        if request.user and request.user.is_authenticated and request.user.role == 'admin':
            return True
        
        # Check if user is the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'customer'):
            return obj.customer.user == request.user
        
        return False
