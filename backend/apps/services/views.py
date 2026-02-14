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
        """List categories (public: active only, admin: all)."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Public endpoints only show active categories
        # Admin endpoints can see all categories
        if request.user.is_authenticated and request.user.role in ['admin', 'manager']:
            # Admin can see all categories (active and inactive)
            is_active = request.query_params.get('is_active')
            if is_active is not None:
                queryset = queryset.filter(is_active=is_active.lower() == 'true')
        else:
            # Public: only active categories
            queryset = queryset.filter(is_active=True)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'meta': {
                'count': queryset.count(),
            }
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='reorder', permission_classes=[IsAdminOrManager])
    def reorder_categories(self, request):
        """
        Update category positions for drag-and-drop ordering.
        POST /api/ad/categories/reorder/
        Body: { "categories": [{"id": 1, "position": 0}, {"id": 2, "position": 1}, ...] }
        """
        categories_data = request.data.get('categories', [])
        
        if not isinstance(categories_data, list):
            return Response({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'categories must be a list',
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        updated_count = 0
        for item in categories_data:
            category_id = item.get('id')
            new_position = item.get('position')
            
            if category_id is None or new_position is None:
                continue
            
            try:
                category = Category.objects.get(id=category_id)
                category.position = new_position
                category.save(update_fields=['position'])
                updated_count += 1
            except Category.DoesNotExist:
                continue
        
        return Response({
            'success': True,
            'data': {
                'updated_count': updated_count,
            },
            'meta': {}
        }, status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve category detail (public)."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data,
            'meta': {}
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
        """List services (public: active only, admin: all)."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Public endpoints only show active services
        # Admin endpoints can see all services
        if request.user.is_authenticated and request.user.role in ['admin', 'manager']:
            # Admin can see all services (active and inactive)
            pass
        else:
            # Public: only active and approved services (staff-created pending are hidden)
            queryset = queryset.filter(is_active=True, approval_status='approved')
        
        # Filter by category if provided
        category_id = request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by postcode if provided (for area-based filtering)
        postcode = request.query_params.get('postcode')
        if postcode:
            # Get services available in this postcode area
            from apps.core.postcode_utils import get_services_for_postcode
            queryset = get_services_for_postcode(postcode)
        
        # Admin can filter by is_active
        if request.user.is_authenticated and request.user.role in ['admin', 'manager']:
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
    
    @action(detail=False, methods=['post'], url_path='reorder', permission_classes=[IsAdminOrManager])
    def reorder(self, request):
        """
        Update service positions for drag-and-drop ordering.
        POST /api/ad/services/reorder/
        Body: { "services": [{"id": 1, "position": 0}, {"id": 2, "position": 1}, ...] }
        """
        services_data = request.data.get('services', [])
        
        if not isinstance(services_data, list):
            return Response({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'services must be a list',
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        updated_count = 0
        for item in services_data:
            service_id = item.get('id')
            new_position = item.get('position')
            
            if service_id is None or new_position is None:
                continue
            
            try:
                service = Service.objects.get(id=service_id)
                service.position = new_position
                service.save(update_fields=['position'])
                updated_count += 1
            except Service.DoesNotExist:
                continue
        
        return Response({
            'success': True,
            'data': {
                'updated_count': updated_count,
            },
            'meta': {}
        }, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        """Create a new service (admin/manager)."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'success': True,
            'data': serializer.data,
            'meta': {'message': 'Service created successfully'}
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update a service (admin/manager)."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'success': True,
            'data': serializer.data,
            'meta': {'message': 'Service updated successfully'}
        }, status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve service detail (public)."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data,
            'meta': {}
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='approve', permission_classes=[IsAdminOrManager])
    def approve(self, request, pk=None):
        """
        Approve a staff-created service (admin/manager).
        POST /api/ad/services/{id}/approve/
        Makes the service visible to customers (approval_status=approved).
        """
        instance = self.get_object()
        if instance.approval_status == 'approved':
            return Response({
                'success': True,
                'data': ServiceListSerializer(instance).data,
                'meta': {'message': 'Service was already approved'}
            }, status=status.HTTP_200_OK)
        instance.approval_status = 'approved'
        instance.save(update_fields=['approval_status'])
        return Response({
            'success': True,
            'data': ServiceListSerializer(instance).data,
            'meta': {'message': 'Service approved; now visible to customers'}
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='by-postcode')
    def by_postcode(self, request):
        """
        Get services available in a postcode area (public).
        GET /api/svc/by-postcode/?postcode=SW1A1AA
        IMPORTANT: Only accepts UK postcodes - VALClean operates only in the UK.
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
        
        # Validate UK postcode (format + country check) - ONCE
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
        
        # OPTIMIZED: Pre-build area coordinates cache to avoid redundant geocoding
        from apps.staff.models import StaffArea, StaffService
        from apps.core.postcode_utils import get_staff_for_postcode, _geocode_postcode_cached
        from django.db.models import Count
        
        # Get all unique postcodes from active areas (geocode once with caching)
        all_areas = StaffArea.objects.filter(
            is_active=True,
            staff__is_active=True
        ).values_list('postcode', flat=True).distinct()
        
        # Geocode all unique postcodes once (with caching - 24h cache)
        area_coords_cache = {}
        for area_postcode in all_areas:
            normalized = area_postcode.upper().replace(' ', '').strip()
            if normalized not in area_coords_cache:
                geocode_result = _geocode_postcode_cached(area_postcode)
                if geocode_result and geocode_result.get('lat') and geocode_result.get('lng'):
                    area_coords_cache[normalized] = {
                        'lat': geocode_result['lat'],
                        'lng': geocode_result['lng']
                    }
                else:
                    area_coords_cache[normalized] = None
        
        # Get available staff ONCE (reused for service filtering and counting)
        available_staff = get_staff_for_postcode(
            validated_postcode,
            validation_result=validation_result,
            area_coords_cache=area_coords_cache
        )
        
        # Get services that have available staff (optimized single query)
        queryset = Service.objects.filter(
            is_active=True,
            approval_status='approved',
            staff_services__staff__in=available_staff,
            staff_services__is_active=True
        ).select_related('category').distinct()
        
        # Pre-calculate staff counts per service (single aggregated query instead of N queries)
        staff_counts = StaffService.objects.filter(
            staff__in=available_staff,
            is_active=True,
            service__in=queryset
        ).values('service_id').annotate(
            staff_count=Count('staff', distinct=True)
        )
        
        # Build staff count lookup map
        staff_count_map = {item['service_id']: item['staff_count'] for item in staff_counts}
        
        # Serialize services with pre-calculated staff counts
        services_data = []
        for service in queryset:
            service_dict = ServiceListSerializer(service).data
            service_dict['available_staff_count'] = staff_count_map.get(service.id, 0)
            services_data.append(service_dict)
        
        return Response({
            'success': True,
            'data': services_data,
            'meta': {
                'postcode': validated_postcode,
                'count': len(services_data),
            }
        }, status=status.HTTP_200_OK)
