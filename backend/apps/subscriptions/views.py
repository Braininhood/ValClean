"""
Subscriptions app views.
Subscription and SubscriptionAppointment viewsets with guest checkout support.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta  # Requires python-dateutil (already in requirements.txt)
from apps.core.permissions import IsCustomer, IsAdminOrManager, IsOwnerOrAdmin
from apps.core.utils import can_cancel_or_reschedule
from .models import Subscription, SubscriptionAppointment
from .serializers import (
    SubscriptionSerializer, SubscriptionListSerializer,
    SubscriptionAppointmentSerializer, SubscriptionCreateSerializer
)
from apps.customers.models import Customer
from apps.services.models import Service
from apps.staff.models import Staff


class SubscriptionPublicViewSet(viewsets.ModelViewSet):
    """
    Public Subscription ViewSet (guest checkout supported).
    Public: POST (create subscription - NO LOGIN REQUIRED)
    GET (by subscription_number or tracking_token - guest access)
    POST /api/bkg/subscriptions/
    GET /api/bkg/guest/subscription/{subscription_number}/
    """
    queryset = Subscription.objects.select_related('service', 'staff', 'customer').prefetch_related(
        'subscription_appointments'
    ).all()
    serializer_class = SubscriptionSerializer
    permission_classes = [AllowAny]  # Public write access for guest checkout
    
    def get_serializer_class(self):
        """Use create serializer for POST, detail serializer for GET."""
        if self.action == 'create':
            return SubscriptionCreateSerializer
        return SubscriptionSerializer
    
    def create(self, request, *args, **kwargs):
        """Create subscription (supports guest checkout)."""
        serializer = SubscriptionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract data
        service_id = serializer.validated_data['service_id']
        staff_id = serializer.validated_data.get('staff_id')
        frequency = serializer.validated_data['frequency']
        duration_months = serializer.validated_data['duration_months']
        start_date = serializer.validated_data['start_date']
        price_per_appointment = serializer.validated_data['price_per_appointment']
        customer_id = serializer.validated_data.get('customer_id')
        
        # Handle guest customer
        customer = None
        if customer_id:
            try:
                customer = Customer.objects.get(id=customer_id)
            except Customer.DoesNotExist:
                pass
        elif serializer.validated_data.get('guest_email'):
            # Create or get guest customer
            guest_email = serializer.validated_data['guest_email']
            guest_name = serializer.validated_data.get('guest_name', '')
            guest_phone = serializer.validated_data.get('guest_phone', '')
            
            customer, created = Customer.objects.get_or_create(
                email=guest_email,
                defaults={
                    'name': guest_name,
                    'phone': guest_phone,
                    'user': None,  # Guest customer, no user account
                }
            )
        
        try:
            service = Service.objects.get(id=service_id, is_active=True)
        except Service.DoesNotExist:
            return Response({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Service not found',
                }
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Assign staff or find available staff
        staff = None
        if staff_id:
            try:
                staff = Staff.objects.get(id=staff_id, is_active=True)
            except Staff.DoesNotExist:
                pass
        
        if not staff:
            # TODO: Auto-assign staff based on postcode/area
            # For now, get first available staff for this service
            staff = Staff.objects.filter(
                is_active=True,
                staff_services__service=service,
                staff_services__is_active=True
            ).first()
        
        # Calculate end_date
        end_date = start_date + relativedelta(months=duration_months)
        
        # Calculate total appointments based on frequency
        total_appointments = 0
        if frequency == 'weekly':
            total_appointments = duration_months * 4
        elif frequency == 'biweekly':
            total_appointments = duration_months * 2
        elif frequency == 'monthly':
            total_appointments = duration_months
        
        # Calculate total price
        total_price = price_per_appointment * total_appointments
        
        # Create subscription
        subscription = Subscription.objects.create(
            customer=customer,
            service=service,
            staff=staff,
            frequency=frequency,
            duration_months=duration_months,
            start_date=start_date,
            end_date=end_date,
            next_appointment_date=start_date,
            status='active',
            total_appointments=total_appointments,
            completed_appointments=0,
            price_per_appointment=price_per_appointment,
            total_price=total_price,
            payment_status='pending',
            cancellation_policy_hours=24,
            # Guest fields
            guest_email=serializer.validated_data.get('guest_email') if not customer or not customer.user else None,
            guest_name=serializer.validated_data.get('guest_name') if not customer or not customer.user else None,
            guest_phone=serializer.validated_data.get('guest_phone') if not customer or not customer.user else None,
            address_line1=serializer.validated_data.get('address_line1'),
            address_line2=serializer.validated_data.get('address_line2'),
            city=serializer.validated_data.get('city'),
            postcode=serializer.validated_data.get('postcode'),
            country=serializer.validated_data.get('country', 'United Kingdom'),
        )
        
        # TODO: Create subscription appointments (schedule all appointments)
        
        # Serialize response
        subscription_serializer = SubscriptionSerializer(subscription)
        
        return Response({
            'success': True,
            'data': subscription_serializer.data,
            'meta': {
                'message': 'Subscription created successfully',
                'guest_checkout': subscription.is_guest_subscription,
                'subscription_number': subscription.subscription_number,
                'tracking_token': subscription.tracking_token,
            }
        }, status=status.HTTP_201_CREATED)


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    Subscription ViewSet (protected - customer/admin/manager).
    Customer: GET own subscriptions, pause, cancel
    Admin/Manager: Full CRUD
    GET, PUT, PATCH, DELETE /api/cus/subscriptions/ or /api/ad/subscriptions/
    """
    queryset = Subscription.objects.select_related('service', 'staff', 'customer').prefetch_related(
        'subscription_appointments'
    ).all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Use simplified serializer for list views."""
        if self.action == 'list':
            return SubscriptionListSerializer
        return SubscriptionSerializer
    
    def get_queryset(self):
        """Filter by current user if customer, or all if admin/manager."""
        queryset = super().get_queryset()
        
        # Customer can only see their own subscriptions
        if self.request.user.role == 'customer':
            try:
                customer = Customer.objects.get(user=self.request.user)
                queryset = queryset.filter(customer=customer)
            except Customer.DoesNotExist:
                queryset = queryset.none()
        
        # Manager can see subscriptions within their scope
        elif self.request.user.role == 'manager':
            # TODO: Implement manager scope filtering
            pass
        
        # Admin can see all subscriptions
        
        # Apply filters
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    def get_permissions(self):
        """Override permissions for write operations."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            if self.request.user.role == 'customer':
                # Customer can only manage their own subscriptions
                return [IsAuthenticated()]
            return [IsAdminOrManager()]
        return [IsAuthenticated()]
    
    @action(detail=True, methods=['post'], url_path='pause')
    def pause(self, request, pk=None):
        """Pause subscription (customer can pause their own subscription)."""
        subscription = self.get_object()
        
        if subscription.status != 'active':
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_STATUS',
                    'message': 'Only active subscriptions can be paused',
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        subscription.status = 'paused'
        subscription.save()
        
        return Response({
            'success': True,
            'data': SubscriptionSerializer(subscription).data,
            'meta': {
                'message': 'Subscription paused successfully',
            }
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """Cancel subscription (customer can cancel their own subscription)."""
        subscription = self.get_object()
        
        if subscription.status in ['cancelled', 'completed']:
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_STATUS',
                    'message': 'Subscription is already cancelled or completed',
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        subscription.status = 'cancelled'
        subscription.save()
        
        return Response({
            'success': True,
            'data': SubscriptionSerializer(subscription).data,
            'meta': {
                'message': 'Subscription cancelled successfully',
            }
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def guest_subscription_view(request, subscription_number):
    """
    Get guest subscription by subscription number (public).
    GET /api/bkg/guest/subscription/{subscription_number}/
    """
    try:
        subscription = Subscription.objects.get(subscription_number=subscription_number)
    except Subscription.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Subscription not found',
            }
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = SubscriptionSerializer(subscription)
    return Response({
        'success': True,
        'data': serializer.data,
        'meta': {}
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def guest_subscription_by_token_view(request, tracking_token):
    """
    Get guest subscription by tracking token (public).
    GET /api/bkg/guest/subscription/token/{tracking_token}/
    """
    try:
        subscription = Subscription.objects.get(tracking_token=tracking_token)
    except Subscription.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Subscription not found',
            }
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = SubscriptionSerializer(subscription)
    return Response({
        'success': True,
        'data': serializer.data,
        'meta': {}
    }, status=status.HTTP_200_OK)
