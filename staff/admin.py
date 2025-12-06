"""
Admin configuration for staff app.
"""
from django.contrib import admin
from .models import Staff, StaffScheduleItem, StaffService, Holiday


class StaffScheduleItemInline(admin.TabularInline):
    model = StaffScheduleItem
    extra = 0


class StaffServiceInline(admin.TabularInline):
    model = StaffService
    extra = 0


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'calendar_provider', 'visibility', 'is_active']
    list_filter = ['calendar_provider', 'visibility', 'is_active']
    search_fields = ['full_name', 'email', 'phone']
    inlines = [StaffScheduleItemInline, StaffServiceInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'full_name', 'email', 'phone', 'photo', 'info')
        }),
        ('Calendar Integration', {
            'fields': ('calendar_provider', 'calendar_id', 'calendar_data')
        }),
        ('Display', {
            'fields': ('visibility', 'position', 'is_active')
        }),
    )


@admin.register(StaffScheduleItem)
class StaffScheduleItemAdmin(admin.ModelAdmin):
    list_display = ['staff', 'day_index', 'start_time', 'end_time']
    list_filter = ['day_index', 'staff']
    ordering = ['staff', 'day_index']


@admin.register(StaffService)
class StaffServiceAdmin(admin.ModelAdmin):
    list_display = ['staff', 'service', 'price', 'capacity', 'deposit']
    list_filter = ['staff', 'service']
    search_fields = ['staff__full_name', 'service__title']


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'staff', 'repeat_event']
    list_filter = ['repeat_event', 'date']
    search_fields = ['name', 'staff__full_name']
    date_hierarchy = 'date'
