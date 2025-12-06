"""
Admin configuration for notifications app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Notification, SentNotification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['type', 'event_type', 'send_to', 'active', 'reminder_info', 'created_at']
    list_filter = ['type', 'event_type', 'send_to', 'active']
    search_fields = ['subject', 'message']
    readonly_fields = ['created_at', 'updated_at', 'placeholders_help']
    fieldsets = (
        ('Notification Information', {
            'fields': ('type', 'event_type', 'send_to', 'active')
        }),
        ('Message', {
            'fields': ('subject', 'message', 'placeholders_help')
        }),
        ('Reminder Settings', {
            'fields': ('reminder_hours_before',),
            'classes': ('collapse',),
            'description': 'For reminder notifications, specify hours before appointment to send.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def reminder_info(self, obj):
        """Display reminder hours if set."""
        if obj.reminder_hours_before:
            return f"{obj.reminder_hours_before} hours before"
        return "-"
    reminder_info.short_description = "Reminder"
    
    def placeholders_help(self, obj):
        """Display available placeholders."""
        placeholders = [
            '{customer_name}', '{customer_email}', '{customer_phone}',
            '{staff_name}', '{staff_email}', '{staff_phone}',
            '{service_name}', '{service_duration}',
            '{appointment_date}', '{appointment_time}', '{appointment_datetime}',
            '{appointment_status}', '{booking_number}',
            '{payment_amount}', '{payment_status}',
            '{cancellation_link}', '{reschedule_link}'
        ]
        help_text = "Available placeholders: " + ", ".join(placeholders)
        return format_html('<div style="background: #f0f0f0; padding: 10px; border-radius: 5px;"><strong>Available Placeholders:</strong><br>{}<br><br><em>Use these placeholders in your message template. They will be replaced with actual values when the notification is sent.</em></div>', ", ".join(placeholders))
    placeholders_help.short_description = "Placeholder Help"


@admin.register(SentNotification)
class SentNotificationAdmin(admin.ModelAdmin):
    list_display = ['notification', 'recipient', 'status_badge', 'sent_at', 'created_at']
    list_filter = ['status', 'sent_at', 'notification__type', 'notification__event_type']
    search_fields = ['recipient', 'notification__subject', 'customer_appointment__id']
    readonly_fields = ['created_at', 'updated_at', 'sent_at']
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Notification Information', {
            'fields': ('notification', 'customer_appointment', 'recipient', 'status')
        }),
        ('Details', {
            'fields': ('sent_at', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def status_badge(self, obj):
        """Display status with color badge."""
        colors = {
            'sent': 'green',
            'failed': 'red',
            'pending': 'orange',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = "Status"
