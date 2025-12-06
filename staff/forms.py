"""
Forms for staff app.
"""
from django import forms
from .models import Staff, StaffScheduleItem, StaffService, Holiday


class StaffForm(forms.ModelForm):
    """Staff form."""
    class Meta:
        model = Staff
        fields = [
            'user', 'full_name', 'email', 'phone', 'photo',
            'info', 'visibility', 'calendar_provider',
            'calendar_id', 'position', 'is_active'
        ]
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'info': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'visibility': forms.Select(attrs={'class': 'form-control'}),
            'calendar_provider': forms.Select(attrs={'class': 'form-control'}),
            'calendar_id': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class StaffScheduleItemForm(forms.ModelForm):
    """Staff schedule item form."""
    class Meta:
        model = StaffScheduleItem
        fields = ['day_index', 'start_time', 'end_time', 'breaks']
        widgets = {
            'day_index': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'breaks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class StaffServiceForm(forms.ModelForm):
    """Staff service form."""
    class Meta:
        model = StaffService
        fields = ['service', 'price', 'capacity', 'deposit']
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'deposit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class HolidayForm(forms.ModelForm):
    """Holiday form."""
    class Meta:
        model = Holiday
        fields = ['staff', 'name', 'date', 'repeat_event']
        widgets = {
            'staff': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'repeat_event': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

