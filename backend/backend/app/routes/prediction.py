from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.models.schemas import PredictionRequest, PredictionResponse
from app.services.prediction_engine import PredictionEngine

router = APIRouter(prefix="/api/v1", tags=["prediction"])

# Initialize prediction engine (singleton)
prediction_engine = PredictionEngine()


@router.post("/predict", response_model=PredictionResponse)
async def create_prediction(request: PredictionRequest):
    """
    Generate probability predictions for a missing person's location.
    
    Returns time-series snapshots showing probability distribution over a grid
    from the time last seen through current time + 12 hours.
    """
    try:
        result = prediction_engine.predict(request)
        return result
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
