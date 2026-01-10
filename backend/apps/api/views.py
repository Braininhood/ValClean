"""
API root view and guest access endpoints.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
# Import guest access views for URL routing
from apps.subscriptions.views import guest_subscription_view, guest_subscription_by_token_view
from apps.orders.views import guest_order_view, guest_order_by_token_view

# Export guest views for URL routing
__all__ = [
    'api_root',
    'guest_subscription_view',
    'guest_subscription_by_token_view',
    'guest_order_view',
    'guest_order_by_token_view',
]


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    API root endpoint showing available API versions and endpoints.
    """
    return Response({
        'success': True,
        'data': {
            'name': 'VALClean Booking System API',
            'version': '1.0.0',
            'endpoints': {
                'documentation': '/api/docs/',
                'schema': '/api/schema/',
                'public': {
                    'services': '/api/svc/',
                    'staff_list': '/api/stf/',
                    'bookings_appointments': '/api/bkg/appointments/',
                    'bookings_subscriptions': '/api/bkg/subscriptions/',
                    'bookings_orders': '/api/bkg/orders/',
                    'address': '/api/addr/',
                    'auth': '/api/aut/',
                    'slots': '/api/slots/',
                    'payments': '/api/pay/',
                },
                'protected': {
                    'customer': '/api/cus/',
                    'staff': '/api/st/',
                    'manager': '/api/man/',
                    'admin': '/api/ad/',
                }
            }
        },
        'meta': {
            'timestamp': None,
        }
    })
