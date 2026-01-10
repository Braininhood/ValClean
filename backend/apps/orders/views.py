"""
Orders app views.
Order and OrderItem viewsets with guest checkout support (multi-service orders).
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from datetime import datetime, timedelta
from apps.core.permissions import IsCustomer, IsAdminOrManager, IsOwnerOrAdmin
from apps.core.utils import can_cancel_or_reschedule
from .models import Order, OrderItem
from .serializers import (
    OrderSerializer, OrderListSerializer, OrderItemSerializer, OrderCreateSerializer
)
from apps.customers.models import Customer
from apps.services.models import Service
from apps.staff.models import Staff


class OrderPublicViewSet(viewsets.ModelViewSet):
    """
    Public Order ViewSet (guest checkout supported - multi-service orders).
    Public: POST (create order - NO LOGIN REQUIRED)
    GET (by order_number or tracking_token - guest access)
    POST /api/bkg/orders/
    GET /api/bkg/guest/order/{order_number}/
    """
    queryset = Order.objects.prefetch_related('items', 'appointments').all()
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]  # Public write access for guest checkout
    
    def get_serializer_class(self):
        """Use create serializer for POST, detail serializer for GET."""
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    def create(self, request, *args, **kwargs):
        """Create multi-service order (supports guest checkout)."""
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract data
        items_data = serializer.validated_data['items']
        scheduled_date = serializer.validated_data['scheduled_date']
        scheduled_time = serializer.validated_data.get('scheduled_time')
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
        
        # Calculate total price
        total_price = 0
        order_items = []
        
        for item_data in items_data:
            service_id = item_data['service_id']
            quantity = item_data.get('quantity', 1)
            staff_id = item_data.get('staff_id')
            
            try:
                service = Service.objects.get(id=service_id, is_active=True)
            except Service.DoesNotExist:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': f'Service with id {service_id} not found',
                    }
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get staff or find available staff
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
            
            unit_price = service.price
            item_total = unit_price * quantity
            total_price += item_total
            
            order_items.append({
                'service': service,
                'staff': staff,
                'quantity': quantity,
                'unit_price': unit_price,
                'total_price': item_total,
            })
        
        # Create order
        order = Order.objects.create(
            customer=customer,
            status='pending',
            total_price=total_price,
            deposit_paid=0,
            payment_status='pending',
            scheduled_date=scheduled_date,
            scheduled_time=scheduled_time,
            cancellation_policy_hours=24,
            # Guest fields
            guest_email=serializer.validated_data.get('guest_email') if not customer or not customer.user else None,
            guest_name=serializer.validated_data.get('guest_name') if not customer or not customer.user else None,
            guest_phone=serializer.validated_data.get('guest_phone') if not customer or not customer.user else None,
            address_line1=serializer.validated_data['address_line1'],
            address_line2=serializer.validated_data.get('address_line2'),
            city=serializer.validated_data['city'],
            postcode=serializer.validated_data['postcode'],
            country=serializer.validated_data.get('country', 'United Kingdom'),
            notes=serializer.validated_data.get('notes'),
        )
        
        # Create order items
        for item_data in order_items:
            OrderItem.objects.create(
                order=order,
                service=item_data['service'],
                staff=item_data['staff'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total_price=item_data['total_price'],
                status='pending',
            )
        
        # Calculate cancellation deadline
        if scheduled_date and scheduled_time:
            scheduled_datetime = timezone.make_aware(
                datetime.combine(scheduled_date, scheduled_time)
            )
            can_cancel_val, can_reschedule_val, deadline = can_cancel_or_reschedule(
                scheduled_datetime,
                order.cancellation_policy_hours
            )
            order.can_cancel = can_cancel_val
            order.can_reschedule = can_reschedule_val
            order.cancellation_deadline = deadline
            order.save()
        
        # Serialize response
        order_serializer = OrderSerializer(order)
        
        return Response({
            'success': True,
            'data': order_serializer.data,
            'meta': {
                'message': 'Order created successfully',
                'guest_checkout': order.is_guest_order,
                'order_number': order.order_number,
                'tracking_token': order.tracking_token,
            }
        }, status=status.HTTP_201_CREATED)


class OrderViewSet(viewsets.ModelViewSet):
    """
    Order ViewSet (protected - customer/admin/manager).
    Customer: GET own orders, cancel, request change
    Admin/Manager: Full CRUD, approve change requests
    GET, PUT, PATCH, DELETE /api/cus/orders/ or /api/ad/orders/
    """
    queryset = Order.objects.select_related('customer').prefetch_related(
        'items', 'appointments'
    ).all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Use simplified serializer for list views."""
        if self.action == 'list':
            return OrderListSerializer
        return OrderSerializer
    
    def get_queryset(self):
        """Filter by current user if customer, or all if admin/manager."""
        queryset = super().get_queryset()
        
        # Customer can only see their own orders
        if self.request.user.role == 'customer':
            try:
                customer = Customer.objects.get(user=self.request.user)
                queryset = queryset.filter(customer=customer)
            except Customer.DoesNotExist:
                queryset = queryset.none()
        
        # Manager can see orders within their scope
        elif self.request.user.role == 'manager':
            # TODO: Implement manager scope filtering
            pass
        
        # Admin can see all orders
        
        # Apply filters
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    def get_permissions(self):
        """Override permissions for write operations."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            if self.request.user.role == 'customer':
                # Customer can only manage their own orders
                return [IsAuthenticated()]
            return [IsAdminOrManager()]
        return [IsAuthenticated()]
    
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """Cancel order (customer can cancel if allowed by 24h policy)."""
        order = self.get_object()
        
        if not order.can_cancel:
            return Response({
                'success': False,
                'error': {
                    'code': 'CANCELLATION_NOT_ALLOWED',
                    'message': f'Cancellation deadline has passed. Deadline was {order.cancellation_deadline}',
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'cancelled'
        order.save()
        
        return Response({
            'success': True,
            'data': OrderSerializer(order).data,
            'meta': {
                'message': 'Order cancelled successfully',
            }
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='request-change')
    def request_change(self, request, pk=None):
        """
        Request date/time change (customer can request change if allowed by 24h policy).
        POST /api/cus/orders/{id}/request-change/
        Body: {"scheduled_date": "2024-01-20", "scheduled_time": "14:00", "notes": "Change request reason"}
        """
        order = self.get_object()
        
        if not order.can_reschedule:
            return Response({
                'success': False,
                'error': {
                    'code': 'RESCHEDULE_NOT_ALLOWED',
                    'message': f'Rescheduling deadline has passed. Deadline was {order.cancellation_deadline}',
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        new_date = request.data.get('scheduled_date')
        new_time = request.data.get('scheduled_time')
        notes = request.data.get('notes', '')
        
        if not new_date:
            return Response({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'scheduled_date is required',
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # TODO: Implement change request workflow (create change request record)
        # For now, update the order directly (admin approval would be needed in production)
        
        from django.utils.dateparse import parse_date, parse_time
        
        order.scheduled_date = parse_date(new_date)
        if new_time:
            order.scheduled_time = parse_time(new_time)
        
        if notes:
            order.notes = f"{order.notes or ''}\n\nChange Request: {notes}".strip()
        
        # Recalculate cancellation deadline
        if order.scheduled_date and order.scheduled_time:
            scheduled_datetime = timezone.make_aware(
                datetime.combine(order.scheduled_date, order.scheduled_time)
            )
            can_cancel_val, can_reschedule_val, deadline = can_cancel_or_reschedule(
                scheduled_datetime,
                order.cancellation_policy_hours
            )
            order.can_cancel = can_cancel_val
            order.can_reschedule = can_reschedule_val
            order.cancellation_deadline = deadline
        
        order.save()
        
        return Response({
            'success': True,
            'data': OrderSerializer(order).data,
            'meta': {
                'message': 'Change request submitted successfully',
            }
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def guest_order_view(request, order_number):
    """
    Get guest order by order number (public).
    GET /api/bkg/guest/order/{order_number}/
    """
    try:
        order = Order.objects.get(order_number=order_number)
    except Order.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Order not found',
            }
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = OrderSerializer(order)
    return Response({
        'success': True,
        'data': serializer.data,
        'meta': {}
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def guest_order_by_token_view(request, tracking_token):
    """
    Get guest order by tracking token (public).
    GET /api/bkg/guest/order/token/{tracking_token}/
    """
    try:
        order = Order.objects.get(tracking_token=tracking_token)
    except Order.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Order not found',
            }
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = OrderSerializer(order)
    return Response({
        'success': True,
        'data': serializer.data,
        'meta': {}
    }, status=status.HTTP_200_OK)
