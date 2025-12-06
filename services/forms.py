"""
Forms for services app.
"""
from django import forms
from .models import Category, Service


class CategoryForm(forms.ModelForm):
    """Category form."""
    class Meta:
        model = Category
        fields = ['name', 'description', 'visibility', 'position', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'visibility': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ServiceForm(forms.ModelForm):
    """Service form."""
    class Meta:
        model = Service
        fields = [
            'category', 'title', 'description', 'duration', 'price',
            'color', 'capacity', 'padding_left', 'padding_right',
            'service_type', 'start_time', 'end_time', 'visibility',
            'position', 'is_active'
        ]
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'padding_left': forms.NumberInput(attrs={'class': 'form-control'}),
            'padding_right': forms.NumberInput(attrs={'class': 'form-control'}),
            'service_type': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'visibility': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

