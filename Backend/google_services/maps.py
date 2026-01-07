import requests
from config import GOOGLE_MAPS_API_KEY


def geocode_address(address: str):
    """
    Geocode an address using Google Maps Geocoding API
    
    Args:
        address: The address to geocode
        
    Returns:
        Geocoding results with lat/lng coordinates
    """
    if not GOOGLE_MAPS_API_KEY:
        return {
            "error": "GOOGLE_MAPS_API_KEY not configured",
            "status": "CONFIG_ERROR",
            "help": "Add GOOGLE_MAPS_API_KEY to your .env file. Get a key from https://console.cloud.google.com/apis/credentials"
        }
    
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": GOOGLE_MAPS_API_KEY}
    response = requests.get(url, params=params)
    return response.json()
