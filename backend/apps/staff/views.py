"""
Staff app views.
Staff, StaffSchedule, StaffService, and StaffArea viewsets.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from apps.core.permissions import IsAdmin, IsAdminOrManager, IsStaff, IsStaffOrManager
from .models import Staff, StaffSchedule, StaffService, StaffArea
from .serializers import (
    StaffSerializer, StaffListSerializer, StaffScheduleSerializer,
    StaffServiceSerializer, StaffAreaSerializer
)


class StaffPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public Staff ViewSet (filtered by postcode/area).
    Public: GET (list by postcode, detail)
    GET /api/stf/
    GET /api/stf/by-postcode/?postcode=SW1A1AA
    """
    queryset = Staff.objects.filter(is_active=True)
    serializer_class = StaffListSerializer
    permission_classes = [AllowAny]
    
    def list(self, request, *args, **kwargs):
        """List staff members (filtered by postcode if provided)."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Filter by postcode if provided
        postcode = request.query_params.get('postcode')
        if postcode:
            # Find staff with service areas covering this postcode
            # TODO: Implement postcode-to-area matching logic
            # For now, return all active staff
            pass
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'meta': {
                'count': queryset.count(),
            }
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='by-postcode')
    def by_postcode(self, request):
        """
        Get staff available in a postcode area (public).
        GET /api/stf/by-postcode/?postcode=SW1A1AA
        """
        postcode = request.query_params.get('postcode')
        if not postcode:
            return Response({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Postcode parameter is required',
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # TODO: Implement postcode-based staff filtering using StaffArea model
        # For now, return all active staff
        queryset = self.get_queryset()
        serializer = StaffListSerializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'meta': {
                'postcode': postcode,
                'count': queryset.count(),
            }
        }, status=status.HTTP_200_OK)


class StaffViewSet(viewsets.ModelViewSet):
    """
    Staff ViewSet (protected - admin/manager).
    GET, POST, PUT, PATCH, DELETE /api/ad/staff/ or /api/man/staff/
    """
    queryset = Staff.objects.select_related('user').prefetch_related(
        'schedules', 'staff_services', 'service_areas'
    ).all()
    serializer_class = StaffSerializer
    permission_classes = [IsAdminOrManager]
    
    def get_serializer_class(self):
        """Use simplified serializer for list views."""
        if self.action == 'list':
            return StaffListSerializer
        return StaffSerializer
    
    def list(self, request, *args, **kwargs):
        """List all staff members."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Filter by active status if provided
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'meta': {
                'count': queryset.count(),
            }
        }, status=status.HTTP_200_OK)


class StaffScheduleViewSet(viewsets.ModelViewSet):
    """
    Staff Schedule ViewSet (protected - staff/admin/manager).
    GET, POST, PUT, PATCH, DELETE /api/st/schedule/ or /api/ad/staff/{id}/schedules/
    """
    queryset = StaffSchedule.objects.select_related('staff').all()
    serializer_class = StaffScheduleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter by current user's staff profile if staff, or all if admin/manager."""
        queryset = super().get_queryset()
        
        # Staff can only see their own schedule
        if self.request.user.role == 'staff':
            try:
                staff = Staff.objects.get(user=self.request.user)
                queryset = queryset.filter(staff=staff)
            except Staff.DoesNotExist:
                queryset = queryset.none()
        # Admin/Manager can see all
        elif self.request.user.role in ['admin', 'manager']:
            # Filter by staff_id if provided
            staff_id = self.request.query_params.get('staff_id')
            if staff_id:
                queryset = queryset.filter(staff_id=staff_id)
        
        return queryset
    
    def get_permissions(self):
        """Override permissions for write operations."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsStaffOrManager()]
        return [IsAuthenticated()]


class StaffAreaViewSet(viewsets.ModelViewSet):
    """
    Staff Service Area ViewSet (protected - admin/manager).
    GET, POST, PUT, PATCH, DELETE /api/ad/staff/{id}/areas/ or /api/man/staff/{id}/areas/
    """
    queryset = StaffArea.objects.select_related('staff').all()
    serializer_class = StaffAreaSerializer
    permission_classes = [IsAdminOrManager]
    
    def get_queryset(self):
        """Filter by staff_id if provided."""
        queryset = super().get_queryset()
        staff_id = self.request.query_params.get('staff_id')
        if staff_id:
            queryset = queryset.filter(staff_id=staff_id)
        return queryset


class StaffServiceViewSet(viewsets.ModelViewSet):
    """
    Staff-Service relationship ViewSet (protected - admin/manager).
    GET, POST, PUT, PATCH, DELETE /api/ad/staff/{id}/services/ or /api/man/staff/{id}/services/
    """
    queryset = StaffService.objects.select_related('staff', 'service').all()
    serializer_class = StaffServiceSerializer
    permission_classes = [IsAdminOrManager]
    
    def get_queryset(self):
        """Filter by staff_id if provided."""
        queryset = super().get_queryset()
        staff_id = self.request.query_params.get('staff_id')
        if staff_id:
            queryset = queryset.filter(staff_id=staff_id)
        return queryset
