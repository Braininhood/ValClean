"""
Admin configuration for customers app.
"""
from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'city', 'country', 'address_validated']
    list_filter = ['country', 'address_validated', 'created_at']
    search_fields = ['name', 'email', 'phone', 'postcode']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'email', 'phone')
        }),
        ('Address', {
            'fields': (
                'address_line1', 'address_line2', 'city', 
                'county', 'postcode', 'country', 'address_validated'
            )
        }),
        ('Additional', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )
