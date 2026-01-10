"""
WebSocket endpoints for real-time prediction streaming.

Allows clients to receive prediction snapshots as they're calculated,
reducing perceived latency and enabling progress updates.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
from datetime import datetime, timedelta
import numpy as np

from app.models.schemas import PredictionRequest
from app.services.prediction_engine import PredictionEngine

router = APIRouter(prefix="/ws", tags=["websocket"])

# Initialize prediction engine
# Set use_elevation_api=True to fetch real elevation from Open-Elevation API
prediction_engine = PredictionEngine(use_elevation_api=True)


@router.websocket("/predict")
async def websocket_predict(websocket: WebSocket):
    """
    WebSocket endpoint for streaming predictions.
    
    Client sends prediction request, server streams back snapshots
    as they're calculated.
    
    Protocol:
    1. Client connects
    2. Client sends JSON prediction request
    3. Server sends progress updates and snapshots
    4. Server sends completion message
    5. Connection closes
    """
    await websocket.accept()
    
    try:
        # Receive prediction request
        data = await websocket.receive_text()
        request_data = json.loads(data)
        
        # Validate and parse request
        try:
            request = PredictionRequest(**request_data)
        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "message": f"Invalid request: {str(e)}"
            })
            await websocket.close()
            return
        
        # Send acknowledgment
        await websocket.send_json({
            "type": "started",
            "message": "Prediction started",
            "request_id": "streaming"
        })
        
        # Stream predictions
        async for snapshot in _stream_prediction(request, websocket):
            await websocket.send_json({
                "type": "snapshot",
                "data": snapshot
            })
        
        # Send completion
        await websocket.send_json({
            "type": "completed",
            "message": "Prediction completed"
        })
        
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Prediction failed: {str(e)}"
            })
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass


async def _stream_prediction(request: PredictionRequest, websocket: WebSocket):
    """
    Generate prediction snapshots and yield them as they're calculated.
    
    This is a streaming version of the prediction engine that sends
    progress updates via WebSocket.
    """
    # Parse time
    time_last_seen = datetime.fromisoformat(request.time_last_seen.replace('Z', '+00:00'))
    current_time = datetime.utcnow()
    
    # Calculate time range
    hours_since_last_seen = (current_time - time_last_seen).total_seconds() / 3600
    total_hours = hours_since_last_seen + 12
    
    # Get terrain (from cache if available)
    terrain = prediction_engine._get_cached_terrain(
        center_lat=request.last_known_location.latitude,
        center_lon=request.last_known_location.longitude,
        radius_km=request.search_radius_km,
        grid_resolution_m=request.grid_resolution_m
    )
    
    # Fetch weather
    weather_data = await prediction_engine.weather_client.get_weather(
        request.last_known_location.latitude,
        request.last_known_location.longitude
    )
    
    # Send progress update
    await websocket.send_json({
        "type": "progress",
        "message": "Terrain and weather data loaded",
        "progress": 0.1
    })
    
    # Initialize probability grid
    start_row, start_col = terrain.lat_lon_to_grid(
        request.last_known_location.latitude,
        request.last_known_location.longitude
    )
    
    probability_grid = np.zeros((terrain.grid_size, terrain.grid_size))
    probability_grid[start_row, start_col] = 1.0
    
    # Generate snapshots
    interval_hours = 0.25
    num_intervals = int(total_hours / interval_hours)
    
    for i in range(num_intervals + 1):
        hours_elapsed = i * interval_hours
        snapshot_time = time_last_seen + timedelta(hours=hours_elapsed)
        
        # Evolve probability
        if i > 0:
            probability_grid = prediction_engine._evolve_probability(
                probability_grid=probability_grid,
                terrain=terrain,
                subject_profile=request.subject_profile,
                hours_elapsed=hours_elapsed,
                interval_hours=interval_hours,
                weather_data=weather_data
            )
        
        # Create snapshot
        snapshot = prediction_engine._create_snapshot(
            probability_grid=probability_grid,
            terrain=terrain,
            timestamp=snapshot_time,
            hours_elapsed=hours_elapsed
        )
        
        # Convert to dict for JSON serialization
        snapshot_dict = {
            "timestamp": snapshot.timestamp,
            "hours_elapsed": snapshot.hours_elapsed,
            "max_probability": snapshot.max_probability,
            "mean_probability": snapshot.mean_probability,
            "grid_cells": [
                {
                    "latitude": cell.latitude,
                    "longitude": cell.longitude,
                    "probability": cell.probability,
                    "elevation": cell.elevation
                }
                for cell in snapshot.grid_cells[:100]  # Limit to top 100 cells for streaming
            ]
        }
        
        yield snapshot_dict
        
        # Send progress update every 10 snapshots
        if i % 10 == 0:
            progress = min((i + 1) / (num_intervals + 1), 0.99)
            await websocket.send_json({
                "type": "progress",
                "message": f"Calculating snapshot {i+1}/{num_intervals+1}",
                "progress": 0.1 + (progress * 0.9)
            })


@router.websocket("/status")
async def websocket_status(websocket: WebSocket):
    """
    Simple WebSocket endpoint for connection testing.
    
    Echoes back status messages.
    """
    await websocket.accept()
    
    try:
        await websocket.send_json({
            "status": "connected",
            "message": "WebSocket connection established"
        })
        
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({
                "status": "ok",
                "echo": data
            })
    
    except WebSocketDisconnect:
        print("Status WebSocket disconnected")
