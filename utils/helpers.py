"""
Helper functions for the FindMyDinner application.
"""
from typing import Dict, List, Any, Optional
import re

def format_place_for_display(place: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a place object for display in the UI.
    
    Args:
        place: The place object from Google Places API
        
    Returns:
        A formatted place object with selected fields
    """
    return {
        "name": place.get("name", "Unknown"),
        "address": place.get("vicinity", "No address available"),
        "rating": place.get("rating", "No rating"),
        "price_level": "$" * place.get("price_level", 0) if place.get("price_level") else "Price not available",
        "place_id": place.get("place_id", ""),
        "types": place.get("types", []),
        "location": place.get("geometry", {}).get("location", {}) if "geometry" in place else {}
    }

def format_place_details(place_details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format detailed place information for display.
    
    Args:
        place_details: The place details from Google Places API
        
    Returns:
        A formatted place details object with selected fields
    """
    # Extract opening hours if available
    opening_hours = {}
    if "opening_hours" in place_details and "weekday_text" in place_details["opening_hours"]:
        opening_hours = {
            "open_now": place_details["opening_hours"].get("open_now", False),
            "weekday_text": place_details["opening_hours"].get("weekday_text", [])
        }
    
    # Format price level
    price_level = place_details.get("price_level", 0)
    price_display = "$" * price_level if price_level else "Price not available"
    
    return {
        "name": place_details.get("name", "Unknown"),
        "address": place_details.get("formatted_address", "No address available"),
        "phone": place_details.get("formatted_phone_number", "No phone number available"),
        "website": place_details.get("website", "No website available"),
        "rating": place_details.get("rating", "No rating"),
        "price_level": price_display,
        "opening_hours": opening_hours,
        "location": place_details.get("geometry", {}).get("location", {}) if "geometry" in place_details else {}
    }

def parse_distance(distance_text: str) -> Optional[int]:
    """
    Parse distance text to get distance in meters.
    
    Args:
        distance_text: Text representation of distance (e.g., "5 km", "500 m")
        
    Returns:
        Distance in meters or None if parsing failed
    """
    # Try to match patterns like "5 km" or "500 m"
    km_match = re.match(r"(\d+(?:\.\d+)?)\s*km", distance_text, re.IGNORECASE)
    m_match = re.match(r"(\d+(?:\.\d+)?)\s*m", distance_text, re.IGNORECASE)
    
    if km_match:
        return int(float(km_match.group(1)) * 1000)
    elif m_match:
        return int(float(m_match.group(1)))
    
    # Try to parse as a plain number (assume meters)
    try:
        return int(float(distance_text))
    except ValueError:
        return None

def filter_places_by_type(places: List[Dict[str, Any]], place_type: str) -> List[Dict[str, Any]]:
    """
    Filter places by type.
    
    Args:
        places: List of places from Google Places API
        place_type: Type to filter by (e.g., "restaurant", "cafe")
        
    Returns:
        Filtered list of places
    """
    if not place_type:
        return places
    
    return [place for place in places if place_type.lower() in [t.lower() for t in place.get("types", [])]]
