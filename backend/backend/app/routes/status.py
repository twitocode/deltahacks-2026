from fastapi import APIRouter
from datetime import datetime

from app.models.schemas import HealthCheckResponse

router = APIRouter(tags=["status"])

VERSION = "0.1.0"


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse(
        status="healthy",
        version=VERSION,
        timestamp=datetime.utcnow().isoformat()
    )


@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Beacon.ai SAR Prediction API",
        "version": VERSION,
        "status": "running",
        "docs": "/docs"
    }
