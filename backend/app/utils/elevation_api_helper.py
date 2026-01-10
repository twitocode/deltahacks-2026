"""
Helper to fetch real elevation data from Open-Elevation API.

This is an async alternative to GeoTIFF files - slower but works anywhere.
"""

import httpx
import numpy as np
import asyncio
from typing import Optional


async def fetch_elevation_grid_from_api(
    center_lat: float,
    center_lon: float,
    radius_km: float,
    grid_size: int,
    max_batch_size: int = 100
) -> np.ndarray:
    """
    Fetch real elevation data from Open-Elevation API for entire grid.
    
    Args:
        center_lat: Center latitude
        center_lon: Center longitude
        radius_km: Search radius in kilometers
        grid_size: Number of grid cells per side
        max_batch_size: Max points per API request (API limit)
        
    Returns:
        2D numpy array of elevations in meters
        
    Note:
        This makes multiple API calls and can be slow for large grids.
        Recommended to use with smaller grids or cache the results.
    """
    # Calculate bounds
    lat_offset = radius_km / 111.0
    lon_offset = radius_km / (111.0 * np.cos(np.radians(center_lat)))
    
    min_lat = center_lat - lat_offset
    max_lat = center_lat + lat_offset
    min_lon = center_lon - lon_offset
    max_lon = center_lon + lon_offset
    
    # Create grid coordinates
    lats = np.linspace(max_lat, min_lat, grid_size)
    lons = np.linspace(min_lon, max_lon, grid_size)
    
    # Build list of all points
    points = []
    for i, lat in enumerate(lats):
        for j, lon in enumerate(lons):
            points.append({
                "latitude": float(lat),
                "longitude": float(lon),
                "i": i,
                "j": j
            })
    
    print(f"📡 Fetching elevation data from API for {len(points)} points...")
    
    # Initialize elevation grid
    elevation_grid = np.zeros((grid_size, grid_size))
    
    # Batch requests to avoid overwhelming API
    async with httpx.AsyncClient() as client:
        for batch_start in range(0, len(points), max_batch_size):
            batch = points[batch_start:batch_start + max_batch_size]
            
            # Prepare API request
            locations = [{"latitude": p["latitude"], "longitude": p["longitude"]} for p in batch]
            
            try:
                response = await client.post(
                    "https://api.open-elevation.com/api/v1/lookup",
                    json={"locations": locations},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    
                    # Fill elevation grid
                    for idx, result in enumerate(results):
                        point = batch[idx]
                        elevation = result.get("elevation", 0.0)
                        elevation_grid[point["i"], point["j"]] = elevation
                    
                    print(f"  ✓ Fetched batch {batch_start // max_batch_size + 1}/{(len(points) + max_batch_size - 1) // max_batch_size}")
                else:
                    print(f"  ✗ API error: {response.status_code}")
                    # Fill with zeros for failed batch
                    for point in batch:
                        elevation_grid[point["i"], point["j"]] = 0.0
                        
            except Exception as e:
                print(f"  ✗ Request failed: {e}")
                # Fill with zeros for failed batch
                for point in batch:
                    elevation_grid[point["i"], point["j"]] = 0.0
            
            # Small delay to be nice to the API
            await asyncio.sleep(0.5)
    
    print(f"✅ Elevation data fetched (min: {elevation_grid.min():.1f}m, max: {elevation_grid.max():.1f}m)")
    return elevation_grid


async def fetch_elevation_point(lat: float, lon: float) -> Optional[float]:
    """
    Fetch elevation for a single point from Open-Elevation API.
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Elevation in meters, or None if failed
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.open-elevation.com/api/v1/lookup",
                json={"locations": [{"latitude": lat, "longitude": lon}]},
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["results"][0]["elevation"]
        except Exception:
            pass
    
    return None


# Example usage
if __name__ == "__main__":
    async def test():
        # Test Banff elevation
        print("Testing Open-Elevation API...")
        elevation = await fetch_elevation_point(51.1784, -115.5708)
        print(f"Banff elevation: {elevation}m")
        
        # Test small grid
        grid = await fetch_elevation_grid_from_api(51.1784, -115.5708, 1.0, 10)
        print(f"Grid shape: {grid.shape}")
        print(f"Grid elevation range: {grid.min():.1f}m to {grid.max():.1f}m")
    
    asyncio.run(test())
