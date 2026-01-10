"""
Elevation data loader for terrain analysis.

Supports loading elevation data from:
1. GeoTIFF files (SRTM, PDEM, etc.)
2. Online elevation APIs (Open-Elevation, Open-Topo-Data)
"""

import numpy as np
from typing import Optional, Tuple
import os
import httpx


class ElevationLoader:
    """Load elevation data from various sources"""
    
    def __init__(self, data_dir: str = "data/elevation"):
        self.data_dir = data_dir
        self.dataset = None
        self._use_rasterio = self._check_rasterio()
    
    def _check_rasterio(self) -> bool:
        """Check if rasterio is available for GeoTIFF reading"""
        try:
            import rasterio
            return True
        except ImportError:
            return False
    
    def load_geotiff(self, tif_path: str):
        """
        Load elevation data from a GeoTIFF file.
        
        Args:
            tif_path: Path to GeoTIFF file
        """
        if not self._use_rasterio:
            raise ImportError(
                "rasterio is required for GeoTIFF support. "
                "Install with: pip install rasterio"
            )
        
        import rasterio
        
        full_path = os.path.join(self.data_dir, tif_path)
        self.dataset = rasterio.open(full_path)
        return self
    
    def get_elevation(self, lat: float, lon: float) -> Optional[float]:
        """
        Get elevation at a specific lat/lon coordinate.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Elevation in meters, or None if unavailable
        """
        if self.dataset:
            return self._get_elevation_from_dataset(lat, lon)
        else:
            # Fallback to synthetic elevation
            return self._synthetic_elevation(lat, lon)
    
    def _get_elevation_from_dataset(self, lat: float, lon: float) -> Optional[float]:
        """Get elevation from loaded rasterio dataset"""
        try:
            row, col = self.dataset.index(lon, lat)
            elevation_array = self.dataset.read(1)
            
            # Check bounds
            if 0 <= row < elevation_array.shape[0] and 0 <= col < elevation_array.shape[1]:
                return float(elevation_array[row, col])
            return None
        except Exception:
            return None
    
    def get_elevation_grid(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float,
        grid_size: int
    ) -> np.ndarray:
        """
        Extract elevation grid for a search area.
        
        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            radius_km: Search radius in kilometers
            grid_size: Number of grid cells per side
            
        Returns:
            2D numpy array of elevations
        """
        if self.dataset:
            return self._extract_grid_from_dataset(
                center_lat, center_lon, radius_km, grid_size
            )
        else:
            return self._generate_synthetic_grid(
                center_lat, center_lon, radius_km, grid_size
            )
    
    def _extract_grid_from_dataset(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float,
        grid_size: int
    ) -> np.ndarray:
        """Extract elevation grid from loaded dataset"""
        # Calculate bounds
        lat_offset = radius_km / 111.0  # Approx 111 km per degree latitude
        lon_offset = radius_km / (111.0 * np.cos(np.radians(center_lat)))
        
        min_lat = center_lat - lat_offset
        max_lat = center_lat + lat_offset
        min_lon = center_lon - lon_offset
        max_lon = center_lon + lon_offset
        
        # Create grid of coordinates
        lats = np.linspace(max_lat, min_lat, grid_size)  # North to south
        lons = np.linspace(min_lon, max_lon, grid_size)  # West to east
        
        elevation_grid = np.zeros((grid_size, grid_size))
        
        for i, lat in enumerate(lats):
            for j, lon in enumerate(lons):
                elevation_grid[i, j] = self.get_elevation(lat, lon) or 0.0
        
        return elevation_grid
    
    def _generate_synthetic_grid(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float,
        grid_size: int
    ) -> np.ndarray:
        """Generate synthetic elevation data for testing"""
        x = np.linspace(-1, 1, grid_size)
        y = np.linspace(-1, 1, grid_size)
        X, Y = np.meshgrid(x, y)
        
        # Create varied terrain with multiple sine waves
        elevation = (
            100 * np.sin(3 * X) * np.cos(3 * Y) +
            50 * np.sin(5 * X + 1) +
            75 * np.cos(4 * Y + 0.5) +
            200  # Base elevation
        )
        
        return elevation
    
    def _synthetic_elevation(self, lat: float, lon: float) -> float:
        """Generate synthetic elevation for a single point"""
        # Simple function based on coordinates
        return 200 + 50 * np.sin(lat * 5) + 50 * np.cos(lon * 5)
    
    async def get_elevation_from_api(
        self,
        lat: float,
        lon: float,
        api: str = "open-elevation"
    ) -> Optional[float]:
        """
        Fetch elevation from online API.
        
        Args:
            lat: Latitude
            lon: Longitude
            api: API to use ('open-elevation' or 'open-topo-data')
            
        Returns:
            Elevation in meters
        """
        if api == "open-elevation":
            url = "https://api.open-elevation.com/api/v1/lookup"
            payload = {"locations": [{"latitude": lat, "longitude": lon}]}
            
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(url, json=payload, timeout=10.0)
                    data = response.json()
                    return data["results"][0]["elevation"]
                except Exception:
                    return None
        
        return None
