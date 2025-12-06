"""
Core models and utilities for the booking system.
"""
from django.db import models
from django.utils import timezone
import uuid


class TimeStampedModel(models.Model):
    """Abstract base model with created and modified timestamps."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """Abstract base model with UUID primary key."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class BaseModel(TimeStampedModel):
    """Base model with timestamps and common fields."""
    is_active = models.BooleanField(default=True)
    position = models.IntegerField(default=9999, help_text="For ordering")

    class Meta:
        abstract = True
        ordering = ['position', 'id']


class SoftDeleteModel(models.Model):
    """Abstract model for soft deletion."""
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Soft delete by setting is_deleted flag."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Restore a soft-deleted object."""
        self.is_deleted = False
        self.deleted_at = None
        self.save()
