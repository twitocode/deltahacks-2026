"""
Data models for the SAR simulation.
"""

from datetime import datetime
from typing import List, Optional, Tuple
from enum import Enum

from pydantic import BaseModel, Field


class Gender(str, Enum):
    """Gender options for hiker profile."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class SearchRequest(BaseModel):
    """Request schema for SAR search simulation."""
    
    latitude: float = Field(..., ge=-90, le=90, description="Last known latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Last known longitude")
    time_last_seen: Optional[datetime] = Field(
        None, 
        description="Time when person was last seen"
    )
    age: Optional[int] = Field(None, description="Age of missing person")
    sex: Optional[str] = Field(None, description="Sex of missing person")
    experience: Optional[str] = Field("novice", description="Experience level: novice, intermediate, experienced, expert")
    
    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 48.3562,
                "longitude": -120.6848,
                "age": 35,
                "sex": "male",
                "experience": "novice",
                "time_last_seen": "2023-10-27T10:00:00Z"
            }
        }


class HeatmapPoint(BaseModel):
    """A single point in the heatmap."""
    latitude: float
    longitude: float
    probability: float


class TimeSlice(BaseModel):
    """Heatmap data for a single time slice."""
    time_offset_minutes: int  # Minutes from last seen time
    points: List[Tuple[float, float, float]] = []  # [(lat, lon, probability), ...]
    grid: Optional[List[List[float]]] = None  # 50x50 probability matrix


class SearchResponse(BaseModel):
    """Response schema for SAR search simulation."""
    
    center_lat: float
    center_lon: float
    radius_km: float
    time_slices: List[TimeSlice]
    
    # Flattened format for frontend compatibility
    heatmap: List[Tuple[float, float, float]] = Field(
        default_factory=list,
        description="Current heatmap as [(lat, lon, intensity), ...]"
    )


class HikerProfile(BaseModel):
    """Profile of missing person affecting simulation behavior."""
    
    age: Optional[int] = None
    gender: Gender = Gender.UNKNOWN
    skill_level: int = 3  # 1-5
    
    @property
    def speed_factor(self) -> float:
        """Base speed modifier based on profile."""
        factor = 1.0
        
        # Age factor
        if self.age:
            if self.age < 18:
                factor *= 0.8
            elif self.age > 60:
                factor *= 0.7
            elif self.age > 70:
                factor *= 0.5
        
        # Skill factor
        factor *= 0.6 + (self.skill_level * 0.1)
        
        return factor
    
    @property
    def direction_randomness(self) -> float:
        """How random/panicked movements are (0=methodical, 1=random)."""
        # Less skilled = more random/panicked movement
        return 1.0 - (self.skill_level - 1) * 0.2
    
    @property
    def trail_preference(self) -> float:
        """Preference for staying on trails (0=ignores, 1=strong)."""
        # More skilled hikers might go off-trail intentionally
        if self.skill_level >= 4:
            return 0.5
        return 0.8


class WeatherConditions(BaseModel):
    """Weather conditions affecting movement."""
    
    temperature_c: float = 15.0  # Celsius
    precipitation_mm: float = 0.0  # mm/hour
    wind_speed_ms: float = 0.0  # m/s
    
    @property
    def movement_penalty(self) -> float:
        """Movement speed penalty from weather (0-1, 0=no penalty)."""
        penalty = 0.0
        
        # Cold penalty
        if self.temperature_c < 0:
            penalty += 0.2
        elif self.temperature_c < -10:
            penalty += 0.4
        
        # Heat penalty
        if self.temperature_c > 30:
            penalty += 0.2
        
        # Precipitation penalty
        if self.precipitation_mm > 0:
            penalty += min(0.3, self.precipitation_mm * 0.05)
        
        # Wind penalty
        if self.wind_speed_ms > 10:
            penalty += 0.1
        
        return min(0.8, penalty)  # Cap at 80% reduction
