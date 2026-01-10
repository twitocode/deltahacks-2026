"""
Weather API client for fetching weather conditions.

Uses Open-Meteo API (no authentication required) to fetch:
- Temperature
- Precipitation
- Wind speed
- Cloud cover

Calculates movement modifiers based on weather conditions.
"""

import httpx
from datetime import datetime
from typing import Optional, Dict
from enum import Enum


class WeatherSeverity(Enum):
    """Weather severity levels"""
    CLEAR = "clear"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    EXTREME = "extreme"


class WeatherClient:
    """Client for fetching weather data and calculating impact on movement"""
    
    BASE_URL = "https://api.open-meteo.com/v1"
    
    def __init__(self):
        self.cache = {}
    
    async def get_weather(
        self,
        lat: float,
        lon: float,
        timestamp: Optional[datetime] = None
    ) -> Optional[Dict]:
        """
        Fetch weather conditions for a location and time.
        
        Args:
            lat: Latitude
            lon: Longitude
            timestamp: Time for weather data (None = current)
            
        Returns:
            Weather data dictionary
        """
        # Create cache key
        cache_key = f"{lat:.4f},{lon:.4f},{timestamp}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        async with httpx.AsyncClient() as client:
            try:
                # Use forecast endpoint
                params = {
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,precipitation,windspeed_10m,cloudcover",
                    "timezone": "auto"
                }
                
                # If historical data needed, use archive API
                # For now, using current/forecast only
                
                response = await client.get(
                    f"{self.BASE_URL}/forecast",
                    params=params,
                    timeout=10.0
                )
                
                data = response.json()
                
                # Cache result
                self.cache[cache_key] = data
                return data
                
            except Exception as e:
                print(f"Failed to fetch weather: {e}")
                return None
    
    def get_movement_modifier(self, weather_data: Optional[Dict]) -> float:
        """
        Calculate movement speed modifier based on weather conditions.
        
        Args:
            weather_data: Weather data from get_weather()
            
        Returns:
            Multiplier for movement speed (0.3 to 1.0)
            1.0 = no impact, 0.3 = severe impact
        """
        if not weather_data or 'current' not in weather_data:
            return 1.0  # No weather data, assume normal conditions
        
        current = weather_data['current']
        modifier = 1.0
        
        # Temperature impact
        temp = current.get('temperature_2m', 15)
        if temp < -10:  # Extreme cold
            modifier *= 0.5
        elif temp < 0:  # Below freezing
            modifier *= 0.7
        elif temp > 35:  # Extreme heat
            modifier *= 0.7
        elif temp > 30:  # High heat
            modifier *= 0.85
        
        # Precipitation impact
        precip = current.get('precipitation', 0)
        if precip > 10:  # Heavy rain
            modifier *= 0.5
        elif precip > 5:  # Moderate rain
            modifier *= 0.7
        elif precip > 1:  # Light rain
            modifier *= 0.9
        
        # Wind speed impact
        wind = current.get('windspeed_10m', 0)
        if wind > 50:  # Extreme wind
            modifier *= 0.6
        elif wind > 30:  # Strong wind
            modifier *= 0.8
        elif wind > 20:  # Moderate wind
            modifier *= 0.9
        
        # Ensure minimum modifier
        return max(modifier, 0.3)
    
    def get_visibility_impact(self, weather_data: Optional[Dict]) -> float:
        """
        Calculate visibility impact on navigation ability.
        
        Poor visibility increases staying-put probability and reduces
        effective movement distance.
        
        Returns:
            Multiplier (0.5 to 1.0), lower = worse visibility
        """
        if not weather_data or 'current' not in weather_data:
            return 1.0
        
        current = weather_data['current']
        visibility = 1.0
        
        # Cloud cover as proxy for visibility
        clouds = current.get('cloudcover', 0)
        if clouds > 90:
            visibility *= 0.8
        elif clouds > 70:
            visibility *= 0.9
        
        # Precipitation reduces visibility
        precip = current.get('precipitation', 0)
        if precip > 5:
            visibility *= 0.6
        elif precip > 1:
            visibility *= 0.8
        
        return max(visibility, 0.5)
    
    def get_exhaustion_rate(self, weather_data: Optional[Dict]) -> float:
        """
        Calculate how quickly exhaustion sets in based on weather.
        
        Returns:
            Multiplier for exhaustion rate (1.0 to 2.0)
            Higher = faster exhaustion
        """
        if not weather_data or 'current' not in weather_data:
            return 1.0
        
        current = weather_data['current']
        exhaustion = 1.0
        
        # Temperature extremes increase exhaustion
        temp = current.get('temperature_2m', 15)
        if temp < -10 or temp > 35:
            exhaustion = 2.0
        elif temp < 0 or temp > 30:
            exhaustion = 1.5
        elif temp < 5 or temp > 28:
            exhaustion = 1.2
        
        # Precipitation increases exhaustion
        precip = current.get('precipitation', 0)
        if precip > 5:
            exhaustion *= 1.3
        elif precip > 1:
            exhaustion *= 1.1
        
        return min(exhaustion, 2.0)
    
    def get_weather_severity(self, weather_data: Optional[Dict]) -> WeatherSeverity:
        """
        Classify overall weather severity.
        
        Returns:
            WeatherSeverity enum value
        """
        if not weather_data or 'current' not in weather_data:
            return WeatherSeverity.CLEAR
        
        current = weather_data['current']
        
        temp = current.get('temperature_2m', 15)
        precip = current.get('precipitation', 0)
        wind = current.get('windspeed_10m', 0)
        
        # Check for extreme conditions
        if temp < -15 or temp > 40 or precip > 15 or wind > 60:
            return WeatherSeverity.EXTREME
        
        # Check for severe conditions
        if temp < -10 or temp > 35 or precip > 10 or wind > 50:
            return WeatherSeverity.SEVERE
        
        # Check for moderate conditions
        if temp < 0 or temp > 30 or precip > 5 or wind > 30:
            return WeatherSeverity.MODERATE
        
        # Check for mild conditions
        if temp < 5 or temp > 28 or precip > 1 or wind > 20:
            return WeatherSeverity.MILD
        
        return WeatherSeverity.CLEAR
    
    def get_weather_summary(self, weather_data: Optional[Dict]) -> str:
        """
        Get human-readable weather summary.
        
        Returns:
            Weather description string
        """
        if not weather_data or 'current' not in weather_data:
            return "Unknown weather conditions"
        
        current = weather_data['current']
        
        temp = current.get('temperature_2m', 'N/A')
        precip = current.get('precipitation', 0)
        wind = current.get('windspeed_10m', 0)
        
        # Build description
        parts = []
        
        if isinstance(temp, (int, float)):
            parts.append(f"{temp:.1f}°C")
        
        if precip > 10:
            parts.append("heavy rain")
        elif precip > 5:
            parts.append("moderate rain")
        elif precip > 1:
            parts.append("light rain")
        
        if wind > 50:
            parts.append("extreme wind")
        elif wind > 30:
            parts.append("strong wind")
        elif wind > 20:
            parts.append("moderate wind")
        
        if not parts:
            return "Clear conditions"
        
        return ", ".join(parts)
    
    def should_shelter(
        self,
        weather_data: Optional[Dict],
        hours_elapsed: float
    ) -> bool:
        """
        Determine if weather conditions would force sheltering.
        
        Args:
            weather_data: Current weather data
            hours_elapsed: Time since last seen
            
        Returns:
            True if conditions likely force staying put
        """
        severity = self.get_weather_severity(weather_data)
        
        # Extreme weather forces shelter regardless of time
        if severity == WeatherSeverity.EXTREME:
            return True
        
        # Severe weather forces shelter after some time
        if severity == WeatherSeverity.SEVERE and hours_elapsed > 2:
            return True
        
        return False
