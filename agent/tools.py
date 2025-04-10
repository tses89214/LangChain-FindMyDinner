"""
Custom LangChain tools for interacting with the Google Places API.
"""
from typing import Optional, ClassVar
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, ConfigDict
from services.places_api import GooglePlacesService
from utils.helpers import format_place_for_display, format_place_details, parse_distance

class FindNearbyRestaurantsInput(BaseModel):
    """Input for FindNearbyRestaurants tool."""
    location: str = Field(..., description="Location to search near (address or 'latitude,longitude')")
    radius: str = Field(default="1000", description="Search radius in meters, or with units like '5 km'")
    keyword: Optional[str] = Field(default=None, description="Optional keyword to filter results (e.g., 'pizza', 'italian')")

class FindNearbyRestaurantsTool(BaseTool):
    """Tool for finding nearby restaurants that are currently open."""
    name: str = "find_nearby_restaurants"
    description: str = "Find restaurants that are currently open near a specified location"
    args_schema: type[FindNearbyRestaurantsInput] = FindNearbyRestaurantsInput
    model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)
    places_service: GooglePlacesService = Field(default=None)
    
    def __init__(self, places_service: Optional[GooglePlacesService] = None):
        """Initialize the tool with a GooglePlacesService instance."""
        super().__init__()
        self.places_service = places_service or GooglePlacesService()
    
    def _run(self, location: str, radius: str = "1000", keyword: Optional[str] = None) -> str:
        """
        Run the tool to find nearby restaurants.
        
        Args:
            location: Location to search near (address or 'latitude,longitude')
            radius: Search radius in meters, or with units like '5 km'
            keyword: Optional keyword to filter results
            
        Returns:
            A string representation of the search results
        """
        # Parse the radius
        radius_meters = parse_distance(radius) or 1000
        
        # Parse the location
        if "," in location and all(part.strip().replace(".", "", 1).replace("-", "", 1).isdigit() 
                                for part in location.split(",")):
            # Looks like "latitude,longitude"
            lat, lng = map(float, location.split(","))
            geo_location = (lat, lng)
        else:
            # Treat as address
            geo_location = self.places_service.geocode_address(location)
            if not geo_location:
                return f"Could not geocode address: {location}"
        
        # Find nearby restaurants
        places = self.places_service.find_nearby_places(
            location=geo_location,
            radius=radius_meters,
            open_now=True,
            type="restaurant",
            keyword=keyword
        )
        
        if not places:
            return f"No open restaurants found near {location} within {radius}"
        
        # Format the results
        formatted_places = [format_place_for_display(place) for place in places]
        
        # Create a readable response
        result = f"Found {len(formatted_places)} open restaurants near {location}:\n\n"
        
        for i, place in enumerate(formatted_places, 1):
            result += f"{i}. {place['name']}\n"
            result += f"   Address: {place['address']}\n"
            result += f"   Rating: {place['rating']} stars\n"
            result += f"   Price: {place['price_level']}\n\n"
        
        result += "To get more details about a specific restaurant, use the get_restaurant_details tool with the place_id."
        
        return result

class GetRestaurantDetailsInput(BaseModel):
    """Input for GetRestaurantDetails tool."""
    place_id: str = Field(..., description="Google Places ID of the restaurant")

class GetRestaurantDetailsTool(BaseTool):
    """Tool for getting detailed information about a specific restaurant."""
    name: str = "get_restaurant_details"
    description: str = "Get detailed information about a specific restaurant by its place_id"
    args_schema: type[GetRestaurantDetailsInput] = GetRestaurantDetailsInput
    model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)
    places_service: GooglePlacesService = Field(default=None)
    
    def __init__(self, places_service: Optional[GooglePlacesService] = None):
        """Initialize the tool with a GooglePlacesService instance."""
        super().__init__()
        self.places_service = places_service or GooglePlacesService()
    
    def _run(self, place_id: str) -> str:
        """
        Run the tool to get restaurant details.
        
        Args:
            place_id: Google Places ID of the restaurant
            
        Returns:
            A string representation of the restaurant details
        """
        # Get place details
        place_details = self.places_service.get_place_details(place_id)
        
        if not place_details:
            return f"No details found for place_id: {place_id}"
        
        # Format the details
        formatted_details = format_place_details(place_details)
        
        # Create a readable response
        result = f"Details for {formatted_details['name']}:\n\n"
        result += f"Address: {formatted_details['address']}\n"
        result += f"Phone: {formatted_details['phone']}\n"
        result += f"Website: {formatted_details['website']}\n"
        result += f"Rating: {formatted_details['rating']} stars\n"
        result += f"Price: {formatted_details['price_level']}\n\n"
        
        # Add opening hours if available
        if formatted_details.get('opening_hours') and formatted_details['opening_hours'].get('weekday_text'):
            result += "Opening Hours:\n"
            for hours in formatted_details['opening_hours']['weekday_text']:
                result += f"- {hours}\n"
        
        return result
