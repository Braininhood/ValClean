"""
Custom middleware for the booking system.
"""
from django.http import HttpResponsePermanentRedirect
from django.conf import settings
from decouple import config


class ForceHTTPSMiddleware:
    """Middleware to force HTTPS for all requests."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip HTTPS redirect in development mode (Django dev server doesn't support SSL)
        # Only enforce HTTPS in production (when DEBUG=False)
        if settings.DEBUG:
            # In development, allow HTTP
            return self.get_response(request)
        
        # Production: Check if request is already HTTPS
        if not request.is_secure():
            # Check if we're behind a proxy (common in production)
            if request.META.get('HTTP_X_FORWARDED_PROTO') == 'https':
                # Proxy says it's HTTPS, so trust it
                return self.get_response(request)
            
            # Redirect to HTTPS
            url = request.build_absolute_uri(request.get_full_path())
            url = url.replace('http://', 'https://', 1)
            return HttpResponsePermanentRedirect(url)
        
        return self.get_response(request)

