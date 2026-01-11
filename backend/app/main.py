"""
Beacon.ai SAR Prediction Backend

FastAPI application for Search and Rescue probability prediction.
"""

import logging
from datetime import datetime
from typing import List, Tuple, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import get_settings
from app.simulation.models import SearchRequest, SearchResponse, TimeSlice, HikerProfile
from app.simulation.simulator import get_simulator
from app.terrain.terrain_pipeline import get_terrain_pipeline
from app.terrain.terrain_sampler import TerrainSampler
from app.dem.dem_loader import get_dem_loader
from app.utils.logging import RequestTimeMiddleware, timed_operation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup
    logger.info("Starting Beacon.ai SAR Prediction Backend")
    settings = get_settings()
    logger.info(f"DEM data directory: {settings.dem_data_path}")
    logger.info(f"Max radius: {settings.max_radius_km}km")
    logger.info(f"Simulation agents: {settings.num_agents}")
    
    # Verify DEM data exists
    if not settings.dem_data_path.exists():
        logger.warning(f"DEM data directory not found: {settings.dem_data_path}")
    else:
        tiles = list(settings.dem_data_path.glob("*.tif"))
        logger.info(f"Found {len(tiles)} DEM tiles")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Beacon.ai SAR Prediction Backend")


# Create FastAPI app
app = FastAPI(
    title="Beacon.ai SAR Prediction API",
    description="Search and Rescue probability prediction using terrain analysis and Monte Carlo simulation",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins + ["*"],  # Allow all origins for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestTimeMiddleware)


# Response Models
class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    dem_tiles: int


class ElevationResponse(BaseModel):
    """Elevation query response."""
    latitude: float
    longitude: float
    elevation_m: Optional[float]


class OriginPoint(BaseModel):
    """Origin point for grid."""
    latitude: float
    longitude: float


class GridMetadata(BaseModel):
    """Metadata for the prediction grid."""
    grid_width: int = 50
    grid_height: int = 50
    cell_size_meters: float = 500.0
    origin: OriginPoint


class SearchResponseV1(BaseModel):
    """Response schema matching frontend API spec."""
    metadata: GridMetadata
    predictions: dict[str, List[List[float]]]  # {"0": [[...]], "1": [[...]], ...}


# Endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with health check."""
    settings = get_settings()
    tiles = list(settings.dem_data_path.glob("*.tif")) if settings.dem_data_path.exists() else []
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        dem_tiles=len(tiles)
    )


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return await root()


@app.post("/api/v1/search", response_model=SearchResponseV1)
async def search_v1(request: SearchRequest):
    """
    Run SAR probability simulation (API v1).
    
    Returns 50x50 probability grid at hour intervals.
    """
    logger.info(
        f"Search request: ({request.latitude:.4f}, {request.longitude:.4f}), "
        f"experience={request.experience}"
    )
    
    try:
        # Map experience to skill level
        experience_map = {
            "novice": 1,
            "intermediate": 2,
            "experienced": 3,
            "expert": 4
        }
        skill_level = experience_map.get(request.experience or "novice", 2)
        
        profile = HikerProfile(
            age=request.age,
            skill_level=skill_level
        )
        
        # Fixed parameters for 50x50 grid with 500m cells = 25km total
        grid_size = 50
        cell_size_m = 500.0
        radius_km = (grid_size * cell_size_m / 2) / 1000.0  # 12.5 km
        
        # Run simulation
        simulator = get_simulator()
        result = await simulator.run_simulation(
            center_lat=request.latitude,
            center_lon=request.longitude,
            radius_km=radius_km,
            profile=profile,
            time_last_seen=request.time_last_seen,
            current_time=datetime.now(),
            grid_size=grid_size  # Pass grid size to simulator
        )
        
        # Convert time slices to minute-keyed predictions (consistent 15-min intervals)
        predictions: dict[str, List[List[float]]] = {}
        # Every 15 minutes from 0 to 480 minutes (8 hours max)
        target_minutes_list = list(range(0, 481, 15))  # [0, 15, 30, ... 480]
        
        for target_minutes in target_minutes_list:
            # Find closest time slice
            best_slice = None
            best_diff = float('inf')
            for ts in result.time_slices:
                diff = abs(ts.time_offset_minutes - target_minutes)
                if diff < best_diff:
                    best_diff = diff
                    best_slice = ts
            
            if best_slice and hasattr(best_slice, 'grid'):
                predictions[str(target_minutes)] = best_slice.grid
            else:
                # Create empty 50x50 grid
                predictions[str(target_minutes)] = [[0.0] * grid_size for _ in range(grid_size)]
        
        logger.info(f"Search complete: generated {len(predictions)} hour predictions")
        
        return SearchResponseV1(
            metadata=GridMetadata(
                grid_width=grid_size,
                grid_height=grid_size,
                cell_size_meters=cell_size_m,
                origin=OriginPoint(
                    latitude=request.latitude,
                    longitude=request.longitude
                )
            ),
            predictions=predictions
        )
        
    except FileNotFoundError as e:
        logger.warning(f"DEM tiles not found: {e}. Returning MOCK data for demo.")
        # Generate mock predictions
        mock_predictions = {}
        target_hours = [0, 1, 3, 6, 12]
        
        # Create a simple Gaussian distribution centered on the start point
        import numpy as np
        
        for hour in target_hours:
            # Spread increases with time
            spread = max(2, hour * 2) 
            
            grid = []
            center_idx = 25 # Center of 50x50 grid
            
            for y in range(50):
                row = []
                for x in range(50):
                    # Distance from center
                    dist = np.sqrt((x - center_idx)**2 + (y - center_idx)**2)
                    # Gaussian
                    val = np.exp(-(dist**2) / (2 * spread**2))
                    row.append(float(val))
                grid.append(row)
            
            mock_predictions[str(hour)] = grid
            
        return SearchResponseV1(
            metadata=GridMetadata(
                grid_width=50,
                grid_height=50,
                cell_size_meters=500.0,
                origin=OriginPoint(
                    latitude=request.latitude,
                    longitude=request.longitude
                )
            ),
            predictions=mock_predictions
        )
    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Simulation error: {e}")


@app.get("/api/elevation", response_model=ElevationResponse)
async def get_elevation(lat: float, lon: float):
    """
    Get elevation for a single point.
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
    
    Returns:
        Elevation in meters
    """
    if not (-90 <= lat <= 90):
        raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
    if not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
    
    try:
        dem_loader = get_dem_loader()
        elevation = dem_loader.get_elevation_at_point(lat, lon)
        
        return ElevationResponse(
            latitude=lat,
            longitude=lon,
            elevation_m=elevation
        )
        
    except Exception as e:
        logger.error(f"Elevation query error: {e}")
        return ElevationResponse(
            latitude=lat,
            longitude=lon,
            elevation_m=None
        )


class TerrainRequest(BaseModel):
    """Request for terrain data."""
    latitude: float
    longitude: float
    radius_km: float = 5.0
    resolution_m: float = 100.0


class TerrainResponse(BaseModel):
    """Terrain grid response."""
    center_lat: float
    center_lon: float
    radius_km: float
    resolution_m: float
    shape: Tuple[int, int]
    bounds: Tuple[float, float, float, float]
    min_elevation: float
    max_elevation: float


@app.post("/api/terrain", response_model=TerrainResponse)
async def get_terrain(request: TerrainRequest):
    """
    Get terrain information for an area.
    
    Returns terrain metadata without the full elevation grid
    (to keep response size reasonable).
    """
    try:
        pipeline = get_terrain_pipeline()
        terrain = pipeline.load_terrain(
            request.latitude,
            request.longitude,
            request.radius_km,
            request.resolution_m
        )
        
        return TerrainResponse(
            center_lat=terrain.center_lat,
            center_lon=terrain.center_lon,
            radius_km=terrain.radius_km,
            resolution_m=terrain.resolution_m,
            shape=terrain.shape,
            bounds=terrain.bounds,
            min_elevation=float(terrain.elevation_grid.min()),
            max_elevation=float(terrain.elevation_grid.max())
        )
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Terrain error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Development entry point
if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
