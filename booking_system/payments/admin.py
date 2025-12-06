"""
Admin configuration for payments app.
"""
from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'status', 'total', 'paid', 'created_at']
    list_filter = ['type', 'status', 'created_at']
    search_fields = ['transaction_id']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Payment Information', {
            'fields': ('type', 'status', 'total', 'paid', 'refund_amount', 'transaction_id')
        }),
        ('Details', {
            'fields': ('details',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
