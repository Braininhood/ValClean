"""
Integration models for third-party services.
"""
from django.db import models
from core.models import BaseModel


class CustomField(BaseModel):
    """Custom field model for booking forms."""
    TYPE_TEXT = 'text'
    TYPE_TEXTAREA = 'textarea'
    TYPE_SELECT = 'select'
    TYPE_CHECKBOX = 'checkbox'
    TYPE_RADIO = 'radio'
    TYPE_DATE = 'date'
    TYPE_FILE = 'file'
    TYPE_CAPTCHA = 'captcha'
    
    TYPE_CHOICES = [
        (TYPE_TEXT, 'Text'),
        (TYPE_TEXTAREA, 'Textarea'),
        (TYPE_SELECT, 'Select'),
        (TYPE_CHECKBOX, 'Checkbox'),
        (TYPE_RADIO, 'Radio'),
        (TYPE_DATE, 'Date'),
        (TYPE_FILE, 'File Upload'),
        (TYPE_CAPTCHA, 'Captcha'),
    ]

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    label = models.CharField(max_length=255)
    required = models.BooleanField(default=False)
    items = models.JSONField(
        default=list,
        blank=True,
        help_text="Options for select/checkbox/radio fields"
    )
    services = models.ManyToManyField(
        'services.Service',
        blank=True,
        related_name='custom_fields',
        help_text="Services this field applies to (empty = all services)"
    )

    class Meta:
        ordering = ['position', 'label']

    def __str__(self):
        return f"{self.label} ({self.get_type_display()})"
