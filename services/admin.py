"""
Admin configuration for services app.
"""
from django.contrib import admin
from .models import Category, Service


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'visibility', 'position', 'is_active']
    list_filter = ['visibility', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['position', 'name']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'duration', 'price', 'capacity', 'service_type', 'is_active']
    list_filter = ['category', 'service_type', 'visibility', 'is_active']
    search_fields = ['title', 'description']
    ordering = ['position', 'title']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'category', 'description', 'service_type')
        }),
        ('Pricing & Duration', {
            'fields': ('duration', 'price', 'capacity', 'padding_left', 'padding_right')
        }),
        ('Display', {
            'fields': ('color', 'visibility', 'position', 'is_active')
        }),
        ('All-Day Service', {
            'fields': ('start_time', 'end_time'),
            'classes': ('collapse',)
        }),
        ('Compound Service', {
            'fields': ('sub_services',),
            'classes': ('collapse',)
        }),
    )
