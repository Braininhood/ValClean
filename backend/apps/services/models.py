"""
Services app models.
Service and Category models.
"""
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class Category(TimeStampedModel):
    """
    Service category (e.g., Cleaning Services, Maintenance, Green Spaces)
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text='Category name'
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        help_text='URL-friendly category name (auto-generated)'
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Category description'
    )
    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True,
        help_text='Category image'
    )
    position = models.IntegerField(
        default=0,
        help_text='Display order (lower numbers appear first)'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Category is active and visible'
    )
    
    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        db_table = 'services_category'
        ordering = ['position', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Service(TimeStampedModel):
    """
    Service model (e.g., Window Cleaning, Grass Cutting, etc.)
    """
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='services',
        help_text='Service category'
    )
    name = models.CharField(
        max_length=200,
        help_text='Service name'
    )
    slug = models.SlugField(
        max_length=200,
        blank=True,
        help_text='URL-friendly service name (auto-generated)'
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Service description'
    )
    
    # Service details
    duration = models.IntegerField(
        help_text='Service duration in minutes'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Base price for this service'
    )
    currency = models.CharField(
        max_length=3,
        default='GBP',
        help_text='Currency code (GBP, USD, etc.)'
    )
    
    # Visual
    image = models.ImageField(
        upload_to='services/',
        blank=True,
        null=True,
        help_text='Service image'
    )
    color = models.CharField(
        max_length=7,
        default='#3B82F6',
        help_text='Color code for calendar/service display (hex)'
    )
    
    # Scheduling
    capacity = models.IntegerField(
        default=1,
        help_text='Number of customers that can book this service simultaneously'
    )
    padding_time = models.IntegerField(
        default=0,
        help_text='Padding time in minutes before next appointment'
    )
    
    # Display
    position = models.IntegerField(
        default=0,
        help_text='Display order (lower numbers appear first)'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Service is active and available for booking'
    )
    
    class Meta:
        verbose_name = 'service'
        verbose_name_plural = 'services'
        db_table = 'services_service'
        ordering = ['position', 'name']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
