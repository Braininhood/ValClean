"""
Address utilities and Google Places API integration.
"""
import requests
from django.conf import settings


def geocode_postcode(postcode):
    """
    Geocode a UK postcode to get latitude and longitude.
    Uses Google Geocoding API or UK Postcodes API.
    
    Args:
        postcode: UK postcode string
    
    Returns:
        dict: {'lat': float, 'lon': float, 'formatted_address': str} or None
    """
    # TODO: Implement Google Geocoding API or UK Postcodes API
    # For now, return None (will be implemented in Week 5)
    return None


def get_address_autocomplete(query, api_key=None):
    """
    Get address suggestions using Google Places API autocomplete.
    
    Args:
        query: Search query string
        api_key: Google Places API key (from settings if not provided)
    
    Returns:
        list: List of address suggestions
    """
    api_key = api_key or settings.GOOGLE_PLACES_API_KEY
    
    if not api_key:
        return []
    
    # TODO: Implement Google Places API autocomplete
    # Will be implemented in Week 3
    url = 'https://maps.googleapis.com/maps/api/place/autocomplete/json'
    params = {
        'input': query,
        'key': api_key,
        'components': 'country:uk',  # UK only
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('predictions', [])
    except Exception as e:
        # Log error but don't break the flow
        pass
    
    return []


def validate_address(address_data):
    """
    Validate address using Google Places API.
    
    Args:
        address_data: Address dictionary
    
    Returns:
        dict: Validated address data or None
    """
    # TODO: Implement Google Places API address validation
    # Will be implemented in Week 3
    return address_data
