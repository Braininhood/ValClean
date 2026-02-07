"""
Postcode utilities for area-based filtering.
Includes distance calculation and postcode-to-area mapping logic.
"""
import math
from typing import List, Optional, Dict, Any
from django.db.models import Q
from apps.core.address import geocode_postcode, validate_postcode_with_google
from apps.staff.models import StaffArea, Staff


def calculate_distance_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula.
    Returns distance in miles (UK standard).
    
    Args:
        lat1, lon1: Latitude and longitude of first point
        lat2, lon2: Latitude and longitude of second point
    
    Returns:
        Distance in miles
    """
    # Earth's radius in miles
    R = 3959.0  # miles
    
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance


# Keep old function name for backward compatibility (converts to miles)
def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    DEPRECATED: Use calculate_distance_miles instead.
    This function now returns miles, not kilometers.
    Kept for backward compatibility.
    """
    return calculate_distance_miles(lat1, lon1, lat2, lon2)


def get_staff_for_postcode(postcode: str, service_id: Optional[int] = None) -> List[Staff]:
    """
    Get staff members who can service a given postcode.
    Uses StaffArea model to check if postcode is within any staff member's service radius.
    When service_id is provided, only areas that apply to that service (or to all services) are considered.
    
    Args:
        postcode: UK postcode string (e.g., 'SW1A 1AA')
        service_id: Optional. If set, only staff with an area covering this postcode for this service are returned.
    
    Returns:
        List of Staff objects that can service this postcode
    """
    # Validate and geocode the postcode
    validation_result = validate_postcode_with_google(postcode)
    
    if not validation_result.get('valid') or not validation_result.get('is_uk'):
        return []
    
    validated_postcode = validation_result.get('formatted', postcode)
    target_lat = validation_result.get('lat')
    target_lng = validation_result.get('lng')
    
    # Base filter: active areas, active staff
    area_filter = dict(is_active=True, staff__is_active=True)
    if service_id is not None:
        # Area applies if service_id is null (all services) or matches this service
        areas_qs = StaffArea.objects.filter(**area_filter).filter(
            Q(service_id__isnull=True) | Q(service_id=service_id)
        ).select_related('staff')
    else:
        areas_qs = StaffArea.objects.filter(**area_filter).select_related('staff')
    
    # If we don't have coordinates, we can't calculate distance
    if target_lat is None or target_lng is None:
        validated_normalized = validated_postcode.upper().replace(' ', '').strip()
        matching_staff_ids = set()
        for area in areas_qs:
            area_normalized = area.postcode.upper().replace(' ', '').strip()
            if area_normalized == validated_normalized:
                matching_staff_ids.add(area.staff_id)
        return Staff.objects.filter(id__in=matching_staff_ids, is_active=True)
    
    available_staff_ids = set()
    for area in areas_qs:
        area_geocode = geocode_postcode(area.postcode)
        if area_geocode and area_geocode.get('lat') and area_geocode.get('lng'):
            area_lat = area_geocode['lat']
            area_lng = area_geocode['lng']
            distance_miles = calculate_distance_miles(target_lat, target_lng, area_lat, area_lng)
            if distance_miles <= float(area.radius_miles):
                available_staff_ids.add(area.staff_id)
        else:
            area_postcode_normalized = area.postcode.upper().replace(' ', '').strip()
            validated_postcode_normalized = validated_postcode.upper().replace(' ', '').strip()
            if area_postcode_normalized == validated_postcode_normalized:
                available_staff_ids.add(area.staff_id)
    
    return Staff.objects.filter(id__in=available_staff_ids, is_active=True).distinct()


def get_services_for_postcode(postcode: str):
    """
    Get services available in a postcode area.
    Only approved services are returned. A service is available if at least one staff
    member who provides that service has an area (per-service or global) covering the postcode.
    
    Args:
        postcode: UK postcode string (e.g., 'SW1A 1AA')
    
    Returns:
        QuerySet of Service objects available in this postcode area
    """
    from apps.services.models import Service
    from apps.staff.models import StaffService
    
    # Get services that are approved and active
    candidate_services = Service.objects.filter(
        is_active=True,
        approval_status='approved'
    )
    
    available_service_ids = []
    for service in candidate_services:
        # Staff must be able to serve this postcode for this specific service (per-service or global area)
        staff_for_service = get_staff_for_postcode(postcode, service_id=service.id)
        if StaffService.objects.filter(
            staff__in=staff_for_service,
            service=service,
            is_active=True
        ).exists():
            available_service_ids.append(service.id)
    
    return Service.objects.filter(id__in=available_service_ids).distinct()


def check_postcode_in_area(customer_postcode: str, staff_area: StaffArea) -> bool:
    """
    Check if a customer postcode is within a staff member's service area.
    
    Args:
        customer_postcode: Customer's postcode
        staff_area: StaffArea object with center postcode and radius
    
    Returns:
        True if customer postcode is within staff area, False otherwise
    """
    # Validate customer postcode
    validation_result = validate_postcode_with_google(customer_postcode)
    
    if not validation_result.get('valid') or not validation_result.get('is_uk'):
        return False
    
    customer_lat = validation_result.get('lat')
    customer_lng = validation_result.get('lng')
    
    # Geocode staff area center postcode
    area_geocode = geocode_postcode(staff_area.postcode)
    
    if not area_geocode or not area_geocode.get('lat') or not area_geocode.get('lng'):
        # Fallback: exact postcode match
        return staff_area.postcode.upper().replace(' ', '') == customer_postcode.upper().replace(' ', '')
    
    area_lat = area_geocode['lat']
    area_lng = area_geocode['lng']
    
    # Calculate distance
    if customer_lat is None or customer_lng is None:
        return False
    
    distance_miles = calculate_distance_miles(customer_lat, customer_lng, area_lat, area_lng)
    
    # Check if within radius (radius_miles is stored in miles)
    return distance_miles <= float(staff_area.radius_miles)
