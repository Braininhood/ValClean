"""
URL configuration for payments app.
"""
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('success/<int:payment_id>/', views.payment_success, name='payment_success'),
    path('cancel/<int:payment_id>/', views.payment_cancel, name='payment_cancel'),
    path('detail/<int:payment_id>/', views.payment_detail, name='payment_detail'),
    # Webhooks
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('webhook/paypal/', views.paypal_webhook, name='paypal_webhook'),
]

