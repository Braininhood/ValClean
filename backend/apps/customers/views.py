"""
Customers app views.
Customer and Address viewsets.
"""
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.core.permissions import IsCustomer, IsAdminOrManager, IsOwnerOrAdmin
from .models import Customer, Address
from .serializers import (
    CustomerSerializer, CustomerListSerializer, AddressSerializer,
    GuestCustomerSerializer
)


class CustomerViewSet(viewsets.ModelViewSet):
    """
    Customer ViewSet (protected - customer/admin/manager).
    Customer: GET own profile, PUT own profile
    Admin/Manager: Full CRUD
    GET, POST, PUT, PATCH, DELETE /api/cus/profile/ or /api/ad/customers/
    """
    queryset = Customer.objects.select_related('user').prefetch_related('addresses').all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Use simplified serializer for list views."""
        if self.action == 'list':
            return CustomerListSerializer
        return CustomerSerializer
    
    def get_queryset(self):
        """Filter by current user if customer, or all if admin/manager."""
        queryset = super().get_queryset()
        
        # Customer can only see their own profile
        if self.request.user.role == 'customer':
            try:
                customer = Customer.objects.get(user=self.request.user)
                queryset = queryset.filter(id=customer.id)
            except Customer.DoesNotExist:
                queryset = queryset.none()
        # Admin/Manager can see all customers
        elif self.request.user.role in ['admin', 'manager']:
            # Apply filters if provided
            email = self.request.query_params.get('email')
            if email:
                queryset = queryset.filter(email__icontains=email)
            postcode = self.request.query_params.get('postcode')
            if postcode:
                queryset = queryset.filter(postcode__icontains=postcode)
        
        return queryset
    
    def get_permissions(self):
        """Override permissions for write operations."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            if self.request.user.role == 'customer':
                # Customer can only update their own profile
                return [IsAuthenticated()]
            return [IsAdminOrManager()]
        return [IsAuthenticated()]
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve customer details."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data,
            'meta': {}
        }, status=status.HTTP_200_OK)
    
    def list(self, request, *args, **kwargs):
        """List customers."""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'meta': {
                'count': queryset.count(),
            }
        }, status=status.HTTP_200_OK)


class AddressViewSet(viewsets.ModelViewSet):
    """
    Address ViewSet (protected - customer/admin/manager).
    Customer: Own addresses CRUD
    Admin/Manager: All addresses CRUD
    GET, POST, PUT, PATCH, DELETE /api/cus/addresses/ or /api/ad/customers/{id}/addresses/
    """
    queryset = Address.objects.select_related('customer').all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter by current user's customer profile if customer, or all if admin/manager."""
        queryset = super().get_queryset()
        
        # Customer can only see their own addresses
        if self.request.user.role == 'customer':
            try:
                customer = Customer.objects.get(user=self.request.user)
                queryset = queryset.filter(customer=customer)
            except Customer.DoesNotExist:
                queryset = queryset.none()
        # Admin/Manager can see all addresses
        elif self.request.user.role in ['admin', 'manager']:
            # Filter by customer_id if provided
            customer_id = self.request.query_params.get('customer_id')
            if customer_id:
                queryset = queryset.filter(customer_id=customer_id)
        
        return queryset
    
    def get_permissions(self):
        """Override permissions for write operations."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            if self.request.user.role == 'customer':
                # Customer can only manage their own addresses
                return [IsAuthenticated()]
            return [IsAdminOrManager()]
        return [IsAuthenticated()]
