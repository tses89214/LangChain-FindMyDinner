"""
Google Places API service for interacting with the Google Places API.
"""
import os
import googlemaps
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GooglePlacesService:
    """
    Service for interacting with the Google Places API.
    """
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Google Places API service.
        
        Args:
            api_key: Google Places API key. If not provided, it will be loaded from environment variables.
        """
        self.api_key = api_key or os.getenv("GOOGLE_PLACES_API_KEY")
        if not self.api_key:
            raise ValueError("Google Places API key is required. Set it in .env file or pass it as an argument.")
        
        self.client = googlemaps.Client(key=self.api_key)
    
    def find_nearby_places(
        self, 
        location: tuple[float, float], 
        radius: int = 1000, 
        open_now: bool = True, 
        type: str = "restaurant",
        keyword: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find nearby places based on location and filters.
        
        Args:
            location: Tuple of (latitude, longitude)
            radius: Search radius in meters
            open_now: Whether to only return places that are currently open
            type: Type of place (e.g., "restaurant", "cafe")
            keyword: Additional keyword to filter results
            
        Returns:
            List of places matching the criteria
        """
        places_result = self.client.places_nearby(
            location=location,
            radius=radius,
            open_now=open_now,
            type=type,
            keyword=keyword
        )
        
        return places_result.get("results", [])
    
    def get_place_details(self, place_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific place.
        
        Args:
            place_id: The Google Places ID of the place
            
        Returns:
            Detailed information about the place
        """
        place_details = self.client.place(
            place_id=place_id,
            fields=[
                "name", "formatted_address", "formatted_phone_number", 
                "opening_hours", "website", "rating", "reviews", 
                "price_level", "photos", "geometry"
            ]
        )
        
        return place_details.get("result", {})
    
    def geocode_address(self, address: str) -> Optional[tuple[float, float]]:
        """
        Convert an address to geographic coordinates.
        
        Args:
            address: The address to geocode
            
        Returns:
            Tuple of (latitude, longitude) or None if geocoding failed
        """
        geocode_result = self.client.geocode(address)
        
        if not geocode_result:
            return None
        
        location = geocode_result[0]["geometry"]["location"]
        return location["lat"], location["lng"]
