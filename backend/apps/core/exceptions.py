"""
Custom exception handlers for Django REST Framework.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger('apps')


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # If response is None, it means Django raised an exception
    if response is not None:
        # Customize the response data structure
        custom_response_data = {
            'success': False,
            'error': {
                'code': response.status_code,
                'message': 'An error occurred',
                'details': response.data if isinstance(response.data, dict) else {'detail': str(response.data)},
            },
            'meta': {
                'timestamp': None,  # Will be set by middleware if needed
            }
        }

        # Handle specific error codes
        if response.status_code == 400:
            custom_response_data['error']['code'] = 'VALIDATION_ERROR'
            custom_response_data['error']['message'] = 'Validation error'
        elif response.status_code == 401:
            custom_response_data['error']['code'] = 'UNAUTHORIZED'
            custom_response_data['error']['message'] = 'Authentication required'
        elif response.status_code == 403:
            custom_response_data['error']['code'] = 'FORBIDDEN'
            custom_response_data['error']['message'] = 'Permission denied'
        elif response.status_code == 404:
            custom_response_data['error']['code'] = 'NOT_FOUND'
            custom_response_data['error']['message'] = 'Resource not found'
        elif response.status_code == 500:
            custom_response_data['error']['code'] = 'SERVER_ERROR'
            custom_response_data['error']['message'] = 'Internal server error'
            logger.error(f"Server error: {exc}", exc_info=True)

        response.data = custom_response_data
    else:
        # Handle Django exceptions that don't have REST framework handlers
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        response = Response(
            {
                'success': False,
                'error': {
                    'code': 'SERVER_ERROR',
                    'message': 'An unexpected error occurred',
                    'details': {'detail': str(exc)},
                },
                'meta': {
                    'timestamp': None,
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response
