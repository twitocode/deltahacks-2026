from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class ExperienceLevel(str, Enum):
    """Hiker experience level"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class Sex(str, Enum):
    """Subject sex for behavioral modeling"""
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class SubjectProfile(BaseModel):
    """Profile of the missing person"""
    age: int = Field(..., ge=1, le=120, description="Age of the subject")
    sex: Sex = Field(default=Sex.UNKNOWN, description="Sex of the subject")
    experience_level: ExperienceLevel = Field(
        default=ExperienceLevel.UNKNOWN,
        description="Hiking experience level"
    )


class Location(BaseModel):
    """GPS coordinates"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class PredictionRequest(BaseModel):
    """Request for probability prediction"""
    last_known_location: Location
    time_last_seen: str = Field(..., description="ISO 8601 timestamp")
    subject_profile: SubjectProfile
    search_radius_km: float = Field(
        default=5.0,
        ge=0.5,
        le=50.0,
        description="Maximum search radius in kilometers"
    )
    grid_resolution_m: float = Field(
        default=100.0,
        ge=10.0,
        le=500.0,
        description="Grid square size in meters"
    )


class GridCell(BaseModel):
    """Single cell in the probability grid"""
    latitude: float
    longitude: float
    probability: float = Field(..., ge=0.0, le=1.0)
    elevation: Optional[float] = None


class TimeSnapshot(BaseModel):
    """Probability distribution at a specific time"""
    timestamp: str  # ISO 8601
    hours_elapsed: float
    grid_cells: List[GridCell]
    max_probability: float
    mean_probability: float


class PredictionResponse(BaseModel):
    """Complete prediction result"""
    request_id: str
    snapshots: List[TimeSnapshot]
    metadata: dict = Field(
        default_factory=dict,
        description="Additional metadata about the prediction"
    )


class SearchRequest(BaseModel):
    """Request matching exact API specification"""
    created_at: str = Field(..., description="ISO 8601 datetime")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    time_last_seen: str = Field(..., description="ISO 8601 datetime")
    age: str = Field(..., description="Age as string")
    gender: str = Field(..., description="male or female")
    skill_level: int = Field(..., ge=1, le=5, description="Skill level 1-5")


class SimpleProbabilityArray(BaseModel):
    """Simplified response with only probability array"""
    probability_grid: List[List[float]] = Field(
        ...,
        description="2D array of probabilities (grid_size x grid_size)"
    )
    grid_info: dict = Field(
        ...,
        description="Grid metadata: center_lat, center_lon, radius_km, resolution_m, grid_size"
    )


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: str
