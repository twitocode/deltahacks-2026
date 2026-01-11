"""
Configuration module for the Beacon.ai SAR Prediction Backend.
Loads environment variables and provides application settings.
"""

import os
from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # DEM data directory (relative to backend folder or absolute path)
    dem_data_dir: str = "../data/elevation/merit"
    
    # Safety limits
    max_radius_km: float = 50.0  # Maximum search radius
    min_grid_resolution_m: float = 30.0  # Minimum grid resolution (DEM native is ~90m)
    default_grid_resolution_m: float = 100.0  # Default grid resolution
    
    # Simulation settings
    num_agents: int = 1000  # Number of Monte Carlo agents
    timestep_minutes: int = 15  # Simulation timestep
    max_simulation_hours: int = 18  # 6 hours before + 12 hours after
    
    # Overpass API for OSM data
    overpass_api_url: str = "https://overpass-api.de/api/interpreter"
    
    # CORS settings
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def dem_data_path(self) -> Path:
        """Get absolute path to DEM data directory."""
        path = Path(self.dem_data_dir)
        if not path.is_absolute():
            # Relative to the backend directory
            backend_dir = Path(__file__).parent.parent
            path = backend_dir / self.dem_data_dir
        return path.resolve()


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
