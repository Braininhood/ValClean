"""
Admin configuration for coupons app.
"""
from django.contrib import admin
from .models import Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount', 'deduction', 'usage_limit', 'used', 'start_date', 'end_date']
    list_filter = ['start_date', 'end_date']
    search_fields = ['code']
    filter_horizontal = ['services']
    readonly_fields = ['created_at', 'updated_at']
