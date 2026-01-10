"""
Services app views.
Service and Category viewsets.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from apps.core.permissions import IsAdmin, IsAdminOrManager
from .models import Category, Service
from .serializers import CategorySerializer, ServiceSerializer, ServiceListSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Category ViewSet.
    Public: GET (list, detail)
    Admin/Manager: POST, PUT, PATCH, DELETE
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]  # Public read access
    
    def get_permissions(self):
        """Override permissions for write operations."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrManager()]
        return [AllowAny()]
    
    def list(self, request, *args, **kwargs):
        """List all active categories (public)."""
        queryset = self.filter_queryset(self.get_queryset().filter(is_active=True))
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'meta': {
                'count': queryset.count(),
            }
        }, status=status.HTTP_200_OK)


class ServiceViewSet(viewsets.ModelViewSet):
    """
    Service ViewSet.
    Public: GET (list, detail, by-postcode)
    Admin/Manager: POST, PUT, PATCH, DELETE
    """
    queryset = Service.objects.select_related('category').all()
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]  # Public read access
    
    def get_serializer_class(self):
        """Use simplified serializer for list views."""
        if self.action == 'list':
            return ServiceListSerializer
        return ServiceSerializer
    
    def get_permissions(self):
        """Override permissions for write operations."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrManager()]
        return [AllowAny()]
    
    def list(self, request, *args, **kwargs):
        """List all active services (public)."""
        queryset = self.filter_queryset(self.get_queryset().filter(is_active=True))
        
        # Filter by category if provided
        category_id = request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by postcode if provided (for area-based filtering)
        postcode = request.query_params.get('postcode')
        if postcode:
            # TODO: Implement postcode-based service filtering
            # For now, return all active services
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
        Get services available in a postcode area (public).
        GET /api/svc/by-postcode/?postcode=SW1A1AA
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
        
        # TODO: Implement postcode-based service filtering
        # For now, return all active services
        queryset = self.get_queryset().filter(is_active=True)
        serializer = ServiceListSerializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'meta': {
                'postcode': postcode,
                'count': queryset.count(),
            }
        }, status=status.HTTP_200_OK)
