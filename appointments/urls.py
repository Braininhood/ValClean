"""
URL configuration for appointments app.
"""
from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    # Booking workflow steps
    path('booking/', views.booking_step1_service, name='booking_step1_service'),
    path('booking/extras/', views.booking_step2_extras, name='booking_step2_extras'),
    path('booking/time/', views.booking_step3_time, name='booking_step3_time'),
    path('booking/repeat/', views.booking_step4_repeat, name='booking_step4_repeat'),
    path('booking/cart/', views.booking_step5_cart, name='booking_step5_cart'),
    path('booking/customer/', views.booking_step6_customer, name='booking_step6_customer'),
    path('booking/payment/', views.booking_step7_payment, name='booking_step7_payment'),
    path('booking/confirmation/', views.booking_step8_confirmation, name='booking_step8_confirmation'),
    # Calendar view
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('view/<str:token>/', views.view_appointment_by_token, name='view_appointment_by_token'),
    path('cancel/<str:token>/', views.cancel_appointment_by_token, name='cancel_appointment_by_token'),
    # Appointment confirmation/approval
    path('confirm/<int:pk>/', views.confirm_appointment, name='confirm_appointment'),
    path('reject/<int:pk>/', views.reject_appointment, name='reject_appointment'),
]

