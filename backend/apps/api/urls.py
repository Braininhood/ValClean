"""
API URL routing with security prefixes.

All endpoints use shortened prefixes for security:
- Public endpoints: /api/svc/, /api/stf/, /api/bkg/, /api/addr/, /api/aut/, /api/slots/, /api/pay/
- Protected endpoints: /api/cus/, /api/st/, /api/man/, /api/ad/
"""
from django.urls import path, include
from . import views
from apps.subscriptions.views import guest_subscription_view, guest_subscription_by_token_view
from apps.orders.views import guest_order_view, guest_order_by_token_view

app_name = 'api'

urlpatterns = [
    # API Root
    path('', views.api_root, name='root'),
    
    # Public Endpoints (Security prefixes)
    path('svc/', include('apps.services.urls')),  # Services (/api/svc/)
    path('aut/', include('apps.accounts.urls')),  # Authentication (/api/aut/)
    path('stf/', include('apps.staff.urls')),  # Staff public listing (/api/stf/)
    path('slots/', include('apps.appointments.urls_slots')),  # Available slots (/api/slots/)
    
    # Bookings/Orders (Public - Guest Checkout Supported)
    # Note: All booking-related endpoints under /api/bkg/ prefix
    path('bkg/appointments/', include('apps.appointments.urls')),  # Appointments (/api/bkg/appointments/)
    path('bkg/subscriptions/', include('apps.subscriptions.urls')),  # Subscriptions (/api/bkg/subscriptions/)
    path('bkg/orders/', include('apps.orders.urls')),  # Orders (/api/bkg/orders/)
    
    # Guest access endpoints (for subscriptions and orders by number/token)
    path('bkg/guest/subscription/<str:subscription_number>/', 
         guest_subscription_view, name='guest-subscription-by-number'),
    path('bkg/guest/subscription/token/<str:tracking_token>/', 
         guest_subscription_by_token_view, name='guest-subscription-by-token'),
    path('bkg/guest/order/<str:order_number>/', 
         guest_order_view, name='guest-order-by-number'),
    path('bkg/guest/order/token/<str:tracking_token>/', 
         guest_order_by_token_view, name='guest-order-by-token'),
    
    # path('addr/', include('apps.core.urls_address')),  # Address (Google Places) - TODO
    # path('pay/', include('apps.payments.urls_public')),  # Payments - TODO
    
    # Protected Endpoints (Role-based security prefixes)
    path('cus/', include('apps.customers.urls_protected')),  # Customer endpoints (/api/cus/)
    # path('st/', include('apps.staff.urls_protected')),  # Staff endpoints - TODO
    # path('man/', include('apps.managers.urls')),  # Manager endpoints - TODO
    # path('ad/', include('apps.admin.urls')),  # Admin endpoints - TODO
]
