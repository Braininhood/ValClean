"""
Appointments app views.
Appointment and CustomerAppointment viewsets with guest checkout support.
"""
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from datetime import datetime, timedelta
from apps.core.permissions import (
    IsCustomer, IsAdminOrManager, IsStaff, IsStaffOrManager, IsOwnerOrAdmin
)
from apps.core.utils import can_cancel_or_reschedule
from .models import Appointment, CustomerAppointment
from .serializers import (
    AppointmentSerializer, CustomerAppointmentSerializer, AppointmentCreateSerializer
)
from apps.customers.models import Customer


class AppointmentPublicViewSet(viewsets.ModelViewSet):
    """
    Public Appointment ViewSet (guest checkout supported).
    Public: POST (create appointment - NO LOGIN REQUIRED)
    GET, POST /api/bkg/
    """
    queryset = Appointment.objects.select_related('staff', 'service').all()
    serializer_class = AppointmentSerializer
    permission_classes = [AllowAny]  # Public write access for guest checkout
    
    def get_serializer_class(self):
        """Use create serializer for POST, detail serializer for GET."""
        if self.action == 'create':
            return AppointmentCreateSerializer
        return AppointmentSerializer
    
    def create(self, request, *args, **kwargs):
        """Create appointment (supports guest checkout)."""
        serializer = AppointmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract data
        service_id = serializer.validated_data['service_id']
        staff_id = serializer.validated_data.get('staff_id')
        start_time = serializer.validated_data['start_time']
        end_time = serializer.validated_data.get('end_time')
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
        
        # Import here to avoid circular imports
        from apps.services.models import Service
        from apps.staff.models import Staff
        
        try:
            service = Service.objects.get(id=service_id)
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
        
        if not staff:
            return Response({
                'success': False,
                'error': {
                    'code': 'NO_STAFF_AVAILABLE',
                    'message': 'No staff available for this service',
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate end_time if not provided
        if not end_time:
            duration = service.duration
            end_time = start_time + timedelta(minutes=duration)
        
        # Create appointment
        appointment = Appointment.objects.create(
            staff=staff,
            service=service,
            start_time=start_time,
            end_time=end_time,
            status='pending',
            appointment_type='single',
        )
        
        # Create customer appointment
        if customer:
            customer_appointment = CustomerAppointment.objects.create(
                customer=customer,
                appointment=appointment,
                number_of_persons=serializer.validated_data.get('number_of_persons', 1),
                extras=serializer.validated_data.get('extras', []),
                custom_fields=serializer.validated_data.get('custom_fields', {}),
                total_price=service.price,  # TODO: Calculate total with extras
                payment_status='pending',
            )
            
            # Calculate cancellation deadline
            can_cancel_val, can_reschedule_val, deadline = can_cancel_or_reschedule(
                start_time,
                customer_appointment.cancellation_policy_hours
            )
            customer_appointment.can_cancel = can_cancel_val
            customer_appointment.can_reschedule = can_reschedule_val
            customer_appointment.cancellation_deadline = deadline
            customer_appointment.save()
        
        # Serialize response
        appointment_serializer = AppointmentSerializer(appointment)
        
        return Response({
            'success': True,
            'data': appointment_serializer.data,
            'meta': {
                'message': 'Appointment created successfully',
                'guest_checkout': customer is None or customer.user is None,
            }
        }, status=status.HTTP_201_CREATED)


class AppointmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Appointment ViewSet (protected - customer/staff/manager/admin).
    Customer: GET own appointments
    Staff: GET assigned appointments
    Manager: GET appointments within scope
    Admin: GET all appointments
    GET /api/cus/appointments/ or /api/st/jobs/ or /api/ad/appointments/
    Note: Write operations handled by AppointmentPublicViewSet or admin endpoints
    """
    queryset = Appointment.objects.select_related('staff', 'service', 'subscription', 'order').prefetch_related(
        'customer_booking'
    ).all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter by user role."""
        queryset = super().get_queryset()
        
        # Customer can only see their own appointments
        if self.request.user.role == 'customer':
            try:
                customer = Customer.objects.get(user=self.request.user)
                customer_appointments = CustomerAppointment.objects.filter(customer=customer)
                appointment_ids = customer_appointments.values_list('appointment_id', flat=True)
                queryset = queryset.filter(id__in=appointment_ids)
            except Customer.DoesNotExist:
                queryset = queryset.none()
        
        # Staff can see their assigned appointments
        elif self.request.user.role == 'staff':
            from apps.staff.models import Staff
            try:
                staff = Staff.objects.get(user=self.request.user)
                queryset = queryset.filter(staff=staff)
            except Staff.DoesNotExist:
                queryset = queryset.none()
        
        # Manager can see appointments within their scope
        elif self.request.user.role == 'manager':
            # TODO: Implement manager scope filtering
            # For now, return all appointments
            pass
        
        # Admin can see all appointments
        
        # Apply filters
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(start_time__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(start_time__lte=date_to)
        
        return queryset
    
    def get_permissions(self):
        """Override permissions for write operations."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrManager()]
        return [IsAuthenticated()]
    
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """
        Cancel appointment (customer can cancel if allowed by 24h policy).
        POST /api/cus/appointments/{id}/cancel/
        """
        appointment = self.get_object()
        
        # Check if customer owns this appointment
        if request.user.role == 'customer':
            try:
                customer = Customer.objects.get(user=request.user)
                customer_appointment = CustomerAppointment.objects.get(
                    customer=customer,
                    appointment=appointment
                )
                
                if not customer_appointment.can_cancel:
                    return Response({
                        'success': False,
                        'error': {
                            'code': 'CANCELLATION_NOT_ALLOWED',
                            'message': f'Cancellation deadline has passed. Deadline was {customer_appointment.cancellation_deadline}',
                        }
                    }, status=status.HTTP_400_BAD_REQUEST)
                
            except CustomerAppointment.DoesNotExist:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': 'Appointment not found or you do not have permission',
                    }
                }, status=status.HTTP_404_NOT_FOUND)
        
        # Cancel appointment
        appointment.status = 'cancelled'
        appointment.save()
        
        return Response({
            'success': True,
            'data': AppointmentSerializer(appointment).data,
            'meta': {
                'message': 'Appointment cancelled successfully',
            }
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='reschedule')
    def reschedule(self, request, pk=None):
        """
        Reschedule appointment (customer can reschedule if allowed by 24h policy).
        POST /api/cus/appointments/{id}/reschedule/
        Body: {"start_time": "2024-01-15T10:00:00Z", "end_time": "2024-01-15T11:00:00Z"}
        """
        appointment = self.get_object()
        new_start_time = request.data.get('start_time')
        new_end_time = request.data.get('end_time')
        
        if not new_start_time:
            return Response({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'start_time is required',
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if customer owns this appointment and can reschedule
        if request.user.role == 'customer':
            try:
                customer = Customer.objects.get(user=request.user)
                customer_appointment = CustomerAppointment.objects.get(
                    customer=customer,
                    appointment=appointment
                )
                
                if not customer_appointment.can_reschedule:
                    return Response({
                        'success': False,
                        'error': {
                            'code': 'RESCHEDULE_NOT_ALLOWED',
                            'message': f'Rescheduling deadline has passed. Deadline was {customer_appointment.cancellation_deadline}',
                        }
                    }, status=status.HTTP_400_BAD_REQUEST)
                
            except CustomerAppointment.DoesNotExist:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': 'Appointment not found or you do not have permission',
                    }
                }, status=status.HTTP_404_NOT_FOUND)
        
        # Reschedule appointment
        from django.utils.dateparse import parse_datetime
        appointment.start_time = parse_datetime(new_start_time)
        if new_end_time:
            appointment.end_time = parse_datetime(new_end_time)
        else:
            # Recalculate end_time based on service duration
            appointment.end_time = appointment.start_time + timedelta(minutes=appointment.service.duration)
        appointment.save()
        
        return Response({
            'success': True,
            'data': AppointmentSerializer(appointment).data,
            'meta': {
                'message': 'Appointment rescheduled successfully',
            }
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def available_slots_view(request):
    """
    Get available time slots by postcode/service/staff (public).
    GET /api/slots/?postcode=SW1A1AA&service_id=1&date=2024-01-15&staff_id=1
    IMPORTANT: Only accepts UK postcodes - VALClean operates only in the UK.
    """
    postcode = request.query_params.get('postcode')
    service_id = request.query_params.get('service_id')
    date = request.query_params.get('date')
    staff_id = request.query_params.get('staff_id')
    
    if not postcode or not service_id or not date:
        return Response({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'postcode, service_id, and date parameters are required',
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate UK postcode (format + country check)
    from apps.core.address import validate_postcode_with_google
    validation_result = validate_postcode_with_google(postcode)
    
    if not validation_result.get('valid') or not validation_result.get('is_uk'):
        error_msg = validation_result.get('error', 'Invalid UK postcode. VALClean currently operates only in the UK.')
        return Response({
            'success': False,
            'error': {
                'code': 'INVALID_POSTCODE',
                'message': error_msg,
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Use validated/formatted postcode
    validated_postcode = validation_result.get('formatted', postcode)
    
    # TODO: Implement available slots calculation based on:
    # 1. Staff schedules for the selected date
    # 2. Existing appointments for the selected date
    # 3. Service duration and padding time
    # 4. Staff availability (breaks, holidays)
    # For now, return a placeholder response
    slots = [
        {'time': '09:00', 'available': True},
        {'time': '10:00', 'available': True},
        {'time': '11:00', 'available': False},
        {'time': '12:00', 'available': False},  # Lunch break
        {'time': '13:00', 'available': False},  # Lunch break
        {'time': '14:00', 'available': True},
        {'time': '15:00', 'available': True},
        {'time': '16:00', 'available': True},
    ]
    
    return Response({
        'success': True,
        'data': {
            'postcode': validated_postcode,
            'service_id': service_id,
            'date': date,
            'staff_id': staff_id,
            'slots': slots,
        },
        'meta': {
            'count': len(slots),
            'available_count': sum(1 for slot in slots if slot['available']),
        }
    }, status=status.HTTP_200_OK)
