"""
Admin configuration for integrations app.
"""
from django.contrib import admin
from .models import CustomField


@admin.register(CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    list_display = ['label', 'type', 'required']
    list_filter = ['type', 'required']
    search_fields = ['label']
    filter_horizontal = ['services']
    ordering = ['label']
