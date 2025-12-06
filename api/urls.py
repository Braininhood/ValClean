"""
API URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Create router for ViewSets
router = DefaultRouter()

# Register viewsets here as they are created
# router.register(r'services', ServiceViewSet)
# router.register(r'staff', StaffViewSet)
# router.register(r'customers', CustomerViewSet)
# router.register(r'appointments', AppointmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Add other API endpoints here
]

