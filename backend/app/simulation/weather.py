"""
Weather Service Module.

Provides weather conditions for simulation (placeholder for demo).
"""

import logging
from datetime import datetime
from typing import Optional

from app.simulation.models import WeatherConditions

logger = logging.getLogger(__name__)


class WeatherService:
    """
    Service for fetching weather conditions.
    
    Currently uses placeholder data based on elevation and time.
    Can be extended to use real weather APIs.
    """
    
    def __init__(self):
        """Initialize the weather service."""
        pass
    
    async def get_conditions(
        self,
        lat: float,
        lon: float,
        timestamp: Optional[datetime] = None,
        elevation_m: Optional[float] = None
    ) -> WeatherConditions:
        """
        Get weather conditions at a location.
        
        Args:
            lat: Latitude
            lon: Longitude
            timestamp: Time for weather (default: now)
            elevation_m: Elevation in meters (for temperature adjustment)
        
        Returns:
            WeatherConditions
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Base temperature (simplified model for demo)
        hour = timestamp.hour
        month = timestamp.month
        
        # Seasonal base (Northern Hemisphere)
        if month in [12, 1, 2]:
            base_temp = -5.0  # Winter
        elif month in [3, 4, 5]:
            base_temp = 10.0  # Spring
        elif month in [6, 7, 8]:
            base_temp = 20.0  # Summer
        else:
            base_temp = 10.0  # Fall
        
        # Diurnal variation
        if 6 <= hour <= 18:
            temp = base_temp + 5.0  # Daytime
        else:
            temp = base_temp - 5.0  # Nighttime
        
        # Elevation adjustment (lapse rate ~6.5°C per 1000m)
        if elevation_m:
            temp -= (elevation_m / 1000.0) * 6.5
        
        # Simple precipitation model (higher probability in mountains)
        precip = 0.0
        if elevation_m and elevation_m > 2000:
            precip = 2.0  # Light rain/snow likelihood
        
        # Wind increases with elevation
        wind = 3.0
        if elevation_m:
            wind += elevation_m / 500.0
        
        conditions = WeatherConditions(
            temperature_c=temp,
            precipitation_mm=precip,
            wind_speed_ms=min(20.0, wind)
        )
        
        logger.debug(
            f"Weather at ({lat:.2f}, {lon:.2f}): "
            f"{conditions.temperature_c:.1f}°C, "
            f"{conditions.precipitation_mm}mm, "
            f"{conditions.wind_speed_ms:.1f}m/s"
        )
        
        return conditions


# Singleton instance
_weather_service: Optional[WeatherService] = None


def get_weather_service() -> WeatherService:
    """Get or create the weather service singleton."""
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherService()
    return _weather_service
