"""
Service and Category models.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel


class Category(BaseModel):
    """Service category model."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    visibility = models.CharField(
        max_length=20,
        choices=[('public', 'Public'), ('private', 'Private')],
        default='public'
    )

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['position', 'name']

    def __str__(self):
        return self.name


class Service(BaseModel):
    """Service model."""
    TYPE_SIMPLE = 'simple'
    TYPE_COMPOUND = 'compound'
    TYPE_CHOICES = [
        (TYPE_SIMPLE, 'Simple'),
        (TYPE_COMPOUND, 'Compound'),
    ]

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='services'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration = models.IntegerField(
        default=900,
        help_text="Duration in minutes (default: 15 minutes)"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    color = models.CharField(
        max_length=7,
        default='#DDDDDD',
        help_text="Hex color code for calendar display"
    )
    capacity = models.IntegerField(
        default=1,
        help_text="Maximum number of persons per appointment"
    )
    padding_left = models.IntegerField(
        default=0,
        help_text="Buffer time before service in minutes"
    )
    padding_right = models.IntegerField(
        default=0,
        help_text="Buffer time after service in minutes"
    )
    service_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=TYPE_SIMPLE
    )
    sub_services = models.JSONField(
        default=list,
        blank=True,
        help_text="List of sub-service IDs for compound services"
    )
    start_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Start time for all-day services"
    )
    end_time = models.TimeField(
        null=True,
        blank=True,
        help_text="End time for all-day services"
    )
    visibility = models.CharField(
        max_length=20,
        choices=[('public', 'Public'), ('private', 'Private')],
        default='public'
    )

    class Meta:
        ordering = ['position', 'title']

    def __str__(self):
        return self.title

    @property
    def is_all_day(self):
        """Check if service is all-day."""
        return self.start_time is not None and self.end_time is not None


class ServiceExtra(BaseModel):
    """Service extra/add-on model."""
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='extras'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    duration = models.IntegerField(
        default=0,
        help_text="Additional duration in minutes (0 if no time added)"
    )
    position = models.IntegerField(
        default=9999,
        help_text="For ordering"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['position', 'title']
        verbose_name_plural = "Service Extras"

    def __str__(self):
        return f"{self.service.title} - {self.title}"