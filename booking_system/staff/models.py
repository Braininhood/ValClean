"""
Staff member models.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from core.models import BaseModel

User = get_user_model()


class Staff(BaseModel):
    """Staff member model."""
    CALENDAR_PROVIDER_CHOICES = [
        ('none', 'None'),
        ('google', 'Google Calendar'),
        ('outlook', 'Microsoft Outlook'),
        ('apple', 'Apple Calendar'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff_profile'
    )
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(
        upload_to='staff/photos/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])]
    )
    info = models.TextField(
        blank=True,
        help_text="Staff bio/information"
    )
    visibility = models.CharField(
        max_length=20,
        choices=[('public', 'Public'), ('private', 'Private')],
        default='public'
    )
    calendar_provider = models.CharField(
        max_length=20,
        choices=CALENDAR_PROVIDER_CHOICES,
        default='none'
    )
    calendar_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="Calendar ID from the provider"
    )
    calendar_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Provider-specific calendar configuration"
    )

    class Meta:
        verbose_name_plural = "Staff"
        ordering = ['position', 'full_name']

    def __str__(self):
        return self.full_name


class StaffScheduleItem(models.Model):
    """Staff weekly schedule item."""
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='schedule_items'
    )
    day_index = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    breaks = models.JSONField(
        default=list,
        blank=True,
        help_text="List of break periods: [{'start': 'HH:MM', 'end': 'HH:MM'}]"
    )

    class Meta:
        unique_together = ['staff', 'day_index']
        ordering = ['day_index', 'start_time']

    def __str__(self):
        return f"{self.staff.full_name} - {self.get_day_index_display()}"


class StaffService(models.Model):
    """Association between staff and services with custom pricing."""
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='staff_services'
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.CASCADE,
        related_name='staff_services'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Custom price for this staff-service combination"
    )
    capacity = models.IntegerField(
        null=True,
        blank=True,
        help_text="Custom capacity for this staff-service combination"
    )
    deposit = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Deposit percentage or fixed amount"
    )

    class Meta:
        unique_together = ['staff', 'service']
        ordering = ['staff', 'service']

    def __str__(self):
        return f"{self.staff.full_name} - {self.service.title}"


class Holiday(models.Model):
    """Holiday model for staff or company-wide."""
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='holidays',
        help_text="Leave null for company-wide holidays"
    )
    name = models.CharField(max_length=255)
    date = models.DateField()
    repeat_event = models.BooleanField(
        default=False,
        help_text="Repeat this holiday yearly"
    )

    class Meta:
        ordering = ['date']

    def __str__(self):
        scope = self.staff.full_name if self.staff else "Company-wide"
        return f"{scope} - {self.name} ({self.date})"
