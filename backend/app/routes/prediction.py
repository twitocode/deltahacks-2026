from fastapi import APIRouter, HTTPException
from datetime import datetime
import numpy as np

from app.models.schemas import (
    PredictionRequest, 
    PredictionResponse,
    SimpleProbabilityArray,
    PredictionRequestSpec
)
from app.services.prediction_engine import PredictionEngine

router = APIRouter(prefix="/api/v1", tags=["prediction"])

# Initialize prediction engine (singleton)
# Set use_elevation_api=True to fetch real elevation from Open-Elevation API
# This is slower but works anywhere without downloading GeoTIFF files
prediction_engine = PredictionEngine(use_elevation_api=True)


@router.post("/predict", response_model=PredictionResponse)
async def create_prediction(request: PredictionRequest):
    """
    Generate probability predictions for a missing person's location.
    
    Returns time-series snapshots showing probability distribution over a grid
    from the time last seen through current time + 12 hours.
    """
    try:
        result = await prediction_engine.predict(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/predict/simple", response_model=SimpleProbabilityArray)
async def create_simple_prediction(request: PredictionRequest):
    """
    Generate probability prediction as a simple 2D array.
    
    Returns only the current probability grid as a 2D array,
    without time-series or detailed metadata.
    
    This is a simplified version for frontend visualization.
    """
    try:
        # Get full prediction
        result = await prediction_engine.predict(request)
        
        # Find the snapshot closest to current time
        # (the one with hours_elapsed closest to hours since last seen)
        from datetime import datetime, timedelta
        time_last_seen = datetime.fromisoformat(request.time_last_seen.replace('Z', '+00:00'))
        current_time = datetime.utcnow()
        hours_since = (current_time - time_last_seen).total_seconds() / 3600
        
        # Find closest snapshot
        closest_snapshot = min(
            result.snapshots,
            key=lambda s: abs(s.hours_elapsed - hours_since)
        )
        
        # Get terrain model to build full grid
        terrain = prediction_engine._get_cached_terrain(
            center_lat=request.last_known_location.latitude,
            center_lon=request.last_known_location.longitude,
            radius_km=request.search_radius_km,
            grid_resolution_m=request.grid_resolution_m
        )
        
        # Create full probability grid
        probability_grid = np.zeros((terrain.grid_size, terrain.grid_size))
        
        # Fill in probabilities from snapshot
        for cell in closest_snapshot.grid_cells:
            row, col = terrain.lat_lon_to_grid(cell.latitude, cell.longitude)
            if terrain.is_valid_cell(row, col):
                probability_grid[row, col] = cell.probability
        
        # Convert to list of lists for JSON
        prob_array = probability_grid.tolist()
        
        return SimpleProbabilityArray(
            probability_grid=prob_array,
            grid_info={
                "center_lat": request.last_known_location.latitude,
                "center_lon": request.last_known_location.longitude,
                "radius_km": request.search_radius_km,
                "resolution_m": request.grid_resolution_m,
                "grid_size": terrain.grid_size,
                "hours_elapsed": closest_snapshot.hours_elapsed
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/predict/array")
async def predict_array_spec(request: PredictionRequestSpec):
    """
    Generate probability prediction matching exact API specification.
    
    Input:
    - created_at: datetime
    - latitude, longitude: floats
    - time_last_seen: datetime  
    - age: string
    - gender: string (male/female)
    - skill_level: int (1-5)
    
    Backend processes: elevation, temperature, precipitation
    
    Response: Dict with time (int) as keys, 2D arrays as values
    {
      0: [[0.0, 0.0, ...], [0.0, 0.0, ...]],
      1: [[0.0, 0.0, ...], [0.0, 0.0, ...]],
      ...
    }
    """
    try:
        # Convert skill_level (1-5) to experience_level
        skill_mapping = {
            1: "low",
            2: "low", 
            3: "medium",
            4: "high",
            5: "expert"
        }
        experience_level = skill_mapping.get(request.skill_level, "medium")
        
        # Convert to internal request format
        internal_request = PredictionRequest(
            last_known_location={"latitude": request.latitude, "longitude": request.longitude},
            time_last_seen=request.time_last_seen,
            subject_profile={
                "age": int(request.age),
                "sex": request.gender,
                "experience_level": experience_level
            },
            search_radius_km=5.0,
            grid_resolution_m=100.0
        )
        
        # Get full prediction
        result = await prediction_engine.predict(internal_request)
        
        # Get terrain for grid info
        terrain = prediction_engine._get_cached_terrain(
            center_lat=request.latitude,
            center_lon=request.longitude,
            radius_km=5.0,
            grid_resolution_m=100.0
        )
        
        # Convert snapshots to time-based dict format
        response_dict = {}
        
        for snapshot in result.snapshots:
            # Use hours_elapsed as integer key
            time_key = int(snapshot.hours_elapsed)
            
            # Create full probability grid for this time
            prob_grid = np.zeros((terrain.grid_size, terrain.grid_size))
            
            for cell in snapshot.grid_cells:
                row, col = terrain.lat_lon_to_grid(cell.latitude, cell.longitude)
                if terrain.is_valid_cell(row, col):
                    prob_grid[row, col] = cell.probability
            
            # Convert to list for JSON
            response_dict[time_key] = prob_grid.tolist()
        
        return response_dict
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@router.get("/predict/{request_id}")
async def get_prediction(request_id: str):
    """
    Retrieve a previously generated prediction by ID.
    
    TODO: Implement caching/storage for predictions
    """
    raise HTTPException(
        status_code=501,
        detail="Prediction retrieval not yet implemented"
    )
