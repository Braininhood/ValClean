"""
Payment views for handling payment processing, webhooks, and callbacks.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

from .models import Payment
from .services import get_payment_service
from appointments.models import CustomerAppointment


@require_http_methods(["GET", "POST"])
def payment_success(request, payment_id):
    """
    Payment success callback.
    Called after successful payment processing.
    """
    try:
        payment = Payment.objects.get(id=payment_id)
        
        # Update payment status if needed
        if payment.status == Payment.STATUS_PENDING:
            payment_service = get_payment_service(payment.type)
            result = payment_service.process_payment(payment.transaction_id)
            
            if result.get('success'):
                payment.status = Payment.STATUS_COMPLETED
                payment.paid = payment.total
                payment.transaction_id = result.get('transaction_id') or payment.transaction_id
                payment.save()
                
                # Update related customer appointments
                customer_appointments = CustomerAppointment.objects.filter(payment=payment)
                for ca in customer_appointments:
                    if ca.status == 'pending':
                        ca.status = 'approved'
                        ca.save()
        
        context = {
            'payment': payment,
        }
        
        return render(request, 'payments/success.html', context)
    except Payment.DoesNotExist:
        messages.error(request, 'Payment not found.')
        return redirect('home')


@require_http_methods(["GET", "POST"])
def payment_cancel(request, payment_id):
    """
    Payment cancellation callback.
    Called when user cancels payment.
    """
    try:
        payment = Payment.objects.get(id=payment_id)
        
        context = {
            'payment': payment,
        }
        
        return render(request, 'payments/cancel.html', context)
    except Payment.DoesNotExist:
        messages.error(request, 'Payment not found.')
        return redirect('home')


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """
    Stripe webhook handler.
    Handles Stripe events (payment_intent.succeeded, payment_intent.payment_failed, etc.)
    """
    # Verify webhook signature
    # Note: In production, verify the webhook signature from Stripe
    # import stripe
    # payload = request.body
    # sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    # event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    
    try:
        import json
        event_data = json.loads(request.body)
        event_type = event_data.get('type')
        event_data_obj = event_data.get('data', {}).get('object', {})
        
        if event_type == 'payment_intent.succeeded':
            payment_intent_id = event_data_obj.get('id')
            
            # Find payment by transaction_id
            try:
                payment = Payment.objects.get(transaction_id=payment_intent_id, type=Payment.TYPE_STRIPE)
                payment.status = Payment.STATUS_COMPLETED
                payment.paid = Decimal(event_data_obj.get('amount', 0)) / 100
                payment.save()
                
                # Update customer appointments
                customer_appointments = CustomerAppointment.objects.filter(payment=payment)
                for ca in customer_appointments:
                    if ca.status == 'pending':
                        ca.status = 'approved'
                        ca.save()
            except Payment.DoesNotExist:
                pass
        
        elif event_type == 'payment_intent.payment_failed':
            payment_intent_id = event_data_obj.get('id')
            
            try:
                payment = Payment.objects.get(transaction_id=payment_intent_id, type=Payment.TYPE_STRIPE)
                payment.status = Payment.STATUS_FAILED
                payment.save()
            except Payment.DoesNotExist:
                pass
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def paypal_webhook(request):
    """
    PayPal webhook handler.
    Handles PayPal IPN (Instant Payment Notification) events.
    """
    try:
        import json
        event_data = json.loads(request.body)
        event_type = event_data.get('event_type')
        
        if event_type == 'PAYMENT.CAPTURE.COMPLETED':
            resource = event_data.get('resource', {})
            capture_id = resource.get('id')
            
            # Find payment by transaction_id
            try:
                payment = Payment.objects.get(transaction_id=capture_id, type=Payment.TYPE_PAYPAL)
                payment.status = Payment.STATUS_COMPLETED
                payment.paid = Decimal(resource.get('amount', {}).get('value', 0))
                payment.save()
                
                # Update customer appointments
                customer_appointments = CustomerAppointment.objects.filter(payment=payment)
                for ca in customer_appointments:
                    if ca.status == 'pending':
                        ca.status = 'approved'
                        ca.save()
            except Payment.DoesNotExist:
                pass
        
        elif event_type == 'PAYMENT.CAPTURE.DENIED':
            resource = event_data.get('resource', {})
            capture_id = resource.get('id')
            
            try:
                payment = Payment.objects.get(transaction_id=capture_id, type=Payment.TYPE_PAYPAL)
                payment.status = Payment.STATUS_FAILED
                payment.save()
            except Payment.DoesNotExist:
                pass
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def payment_detail(request, payment_id):
    """View payment details (for customers and staff)."""
    payment = get_object_or_404(Payment, id=payment_id)
    
    # Check permissions
    if request.user.is_superuser or request.user.role == 'admin':
        pass  # Admin can view any payment
    elif request.user.role == 'customer':
        # Customer can only view their own payments
        customer_appointments = CustomerAppointment.objects.filter(
            payment=payment,
            customer__user=request.user
        )
        if not customer_appointments.exists():
            messages.error(request, 'You do not have permission to view this payment.')
            return redirect('customers:customer_dashboard')
    elif request.user.role == 'staff':
        # Staff can view payments for their appointments
        from staff.models import Staff
        try:
            staff = Staff.objects.get(user=request.user)
            customer_appointments = CustomerAppointment.objects.filter(
                payment=payment,
                appointment__staff=staff
            )
            if not customer_appointments.exists():
                messages.error(request, 'You do not have permission to view this payment.')
                return redirect('staff:staff_dashboard')
        except Staff.DoesNotExist:
            messages.error(request, 'Staff profile not found.')
            return redirect('staff:staff_dashboard')
    else:
        messages.error(request, 'You do not have permission to view this payment.')
        return redirect('home')
    
    context = {
        'payment': payment,
    }
    
    return render(request, 'payments/detail.html', context)
