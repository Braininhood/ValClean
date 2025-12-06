"""
Admin configuration for appointments app.
"""
from django.contrib import admin
from .models import Appointment, CustomerAppointment, Series


class CustomerAppointmentInline(admin.TabularInline):
    model = CustomerAppointment
    extra = 0
    readonly_fields = ['token', 'created_at']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['service', 'staff', 'start_date', 'end_date', 'calendar_provider', 'created_at']
    list_filter = ['calendar_provider', 'start_date', 'service', 'staff']
    search_fields = ['service__title', 'staff__full_name', 'internal_note']
    date_hierarchy = 'start_date'
    inlines = [CustomerAppointmentInline]
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Appointment Details', {
            'fields': ('staff', 'service', 'start_date', 'end_date', 'series')
        }),
        ('Calendar Integration', {
            'fields': ('calendar_provider', 'calendar_event_id')
        }),
        ('Additional', {
            'fields': ('internal_note', 'extras_duration', 'created_at', 'updated_at')
        }),
    )


@admin.register(CustomerAppointment)
class CustomerAppointmentAdmin(admin.ModelAdmin):
    list_display = ['customer', 'appointment', 'status', 'number_of_persons', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer__name', 'customer__email', 'token']
    readonly_fields = ['token', 'compound_token', 'created_at', 'updated_at']
    date_hierarchy = 'appointment__start_date'


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ['id', 'repeat_type', 'repeat_interval', 'until_date', 'occurrences']
    list_filter = ['repeat_type']
