"""
URL configuration for calendar_sync app.
"""
from django.urls import path
from . import views

app_name = 'calendar_sync'

urlpatterns = [
    # Google Calendar
    path('google/connect/', views.connect_google_calendar, name='connect_google'),
    path('google/callback/', views.google_calendar_callback, name='google_callback'),
    
    # Microsoft Outlook Calendar
    path('outlook/connect/', views.connect_outlook_calendar, name='connect_outlook'),
    path('outlook/callback/', views.outlook_calendar_callback, name='outlook_callback'),
    
    # General
    path('disconnect/', views.disconnect_calendar, name='disconnect'),
    path('ical/<int:appointment_id>/', views.download_ical, name='download_ical'),
]

