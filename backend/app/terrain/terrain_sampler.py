"""
Terrain Sampler Module.

Provides efficient elevation and slope sampling from a TerrainModel.
"""

import logging
from typing import Optional, Tuple
import math

import numpy as np
from scipy import ndimage

from app.terrain.terrain_pipeline import TerrainModel

logger = logging.getLogger(__name__)


class TerrainSampler:
    """
    Efficient sampler for terrain elevation and slope.
    
    Provides bilinear interpolation for elevation queries and
    gradient calculations for slope.
    """
    
    def __init__(self, terrain: TerrainModel):
        """
        Initialize the terrain sampler.
        
        Args:
            terrain: TerrainModel with elevation data
        """
        self.terrain = terrain
        self._elevation = terrain.elevation_grid
        self._bounds = terrain.bounds
        self._shape = terrain.shape
        
        # Pre-compute coordinate conversion factors
        west, south, east, north = self._bounds
        rows, cols = self._shape
        
        self._lon_per_col = (east - west) / cols
        self._lat_per_row = (north - south) / rows
        
        # Pre-compute slope grids
        self._slope_x: Optional[np.ndarray] = None
        self._slope_y: Optional[np.ndarray] = None
        self._slope_magnitude: Optional[np.ndarray] = None
        
        logger.debug(f"TerrainSampler initialized for {rows}x{cols} grid")
    
    def _latlon_to_rowcol(
        self, 
        lat: float, 
        lon: float
    ) -> Tuple[float, float]:
        """
        Convert lat/lon to fractional row/col indices.
        
        Args:
            lat: Latitude
            lon: Longitude
        
        Returns:
            (row, col) as floats for interpolation
        """
        west, south, east, north = self._bounds
        rows, cols = self._shape
        
        # Compute fractional indices (0-indexed from top-left)
        col = (lon - west) / self._lon_per_col
        row = (north - lat) / self._lat_per_row  # Note: row increases southward
        
        return row, col
    
    def _is_in_bounds(self, lat: float, lon: float) -> bool:
        """Check if point is within terrain bounds."""
        west, south, east, north = self._bounds
        return south <= lat <= north and west <= lon <= east
    
    def elevation(
        self, 
        lat: float, 
        lon: float,
        interpolate: bool = True
    ) -> Optional[float]:
        """
        Get elevation at a point using bilinear interpolation.
        
        Args:
            lat: Latitude
            lon: Longitude
            interpolate: Whether to use bilinear interpolation
        
        Returns:
            Elevation in meters, or None if out of bounds
        """
        if not self._is_in_bounds(lat, lon):
            return None
        
        row, col = self._latlon_to_rowcol(lat, lon)
        rows, cols = self._shape
        
        if interpolate:
            # Bilinear interpolation
            r0, c0 = int(row), int(col)
            r1, c1 = min(r0 + 1, rows - 1), min(c0 + 1, cols - 1)
            
            # Clamp to valid range
            r0 = max(0, min(r0, rows - 1))
            c0 = max(0, min(c0, cols - 1))
            
            # Fractional parts
            dr = row - r0
            dc = col - c0
            
            # Get corner values
            v00 = self._elevation[r0, c0]
            v01 = self._elevation[r0, c1]
            v10 = self._elevation[r1, c0]
            v11 = self._elevation[r1, c1]
            
            # Bilinear interpolation
            value = (
                v00 * (1 - dr) * (1 - dc) +
                v01 * (1 - dr) * dc +
                v10 * dr * (1 - dc) +
                v11 * dr * dc
            )
            
            return float(value)
        else:
            # Nearest neighbor
            r, c = int(round(row)), int(round(col))
            r = max(0, min(r, rows - 1))
            c = max(0, min(c, cols - 1))
            return float(self._elevation[r, c])
    
    def _compute_slope_grids(self) -> None:
        """Pre-compute slope gradient grids."""
        if self._slope_magnitude is not None:
            return
        
        # Compute gradients using Sobel filter
        # Cell size in meters (approximate)
        cell_size_m = self.terrain.resolution_m
        
        # Gradient in x (east-west) and y (north-south) directions
        self._slope_y, self._slope_x = np.gradient(
            self._elevation, 
            cell_size_m
        )
        
        # Magnitude of slope (rise over run)
        self._slope_magnitude = np.sqrt(
            self._slope_x**2 + self._slope_y**2
        )
        
        logger.debug("Computed slope grids")
    
    def slope(
        self, 
        lat1: float, 
        lon1: float, 
        lat2: float, 
        lon2: float
    ) -> Optional[float]:
        """
        Calculate slope between two points.
        
        Args:
            lat1, lon1: Start point
            lat2, lon2: End point
        
        Returns:
            Slope as rise/run (positive = uphill), or None if either point out of bounds
        """
        elev1 = self.elevation(lat1, lon1)
        elev2 = self.elevation(lat2, lon2)
        
        if elev1 is None or elev2 is None:
            return None
        
        # Calculate horizontal distance (Haversine approximation)
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        lat_mid = math.radians((lat1 + lat2) / 2)
        
        # Approximate meters
        dx = dlon * 6371000 * math.cos(lat_mid)
        dy = dlat * 6371000
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < 0.1:  # Less than 10cm
            return 0.0
        
        rise = elev2 - elev1
        return rise / distance
    
    def slope_at_point(self, lat: float, lon: float) -> Optional[float]:
        """
        Get slope magnitude at a point.
        
        Args:
            lat: Latitude
            lon: Longitude
        
        Returns:
            Slope magnitude (rise/run), or None if out of bounds
        """
        if not self._is_in_bounds(lat, lon):
            return None
        
        self._compute_slope_grids()
        
        row, col = self._latlon_to_rowcol(lat, lon)
        r, c = int(round(row)), int(round(col))
        r = max(0, min(r, self._shape[0] - 1))
        c = max(0, min(c, self._shape[1] - 1))
        
        return float(self._slope_magnitude[r, c])
    
    def slope_direction(
        self, 
        lat: float, 
        lon: float
    ) -> Optional[Tuple[float, float]]:
        """
        Get slope direction (downhill) at a point.
        
        Args:
            lat: Latitude
            lon: Longitude
        
        Returns:
            (dx, dy) unit vector pointing downhill, or None if out of bounds
        """
        if not self._is_in_bounds(lat, lon):
            return None
        
        self._compute_slope_grids()
        
        row, col = self._latlon_to_rowcol(lat, lon)
        r, c = int(round(row)), int(round(col))
        r = max(0, min(r, self._shape[0] - 1))
        c = max(0, min(c, self._shape[1] - 1))
        
        # Downhill direction is negative gradient
        dx = -self._slope_x[r, c]
        dy = -self._slope_y[r, c]
        
        # Normalize
        mag = math.sqrt(dx**2 + dy**2)
        if mag < 1e-6:
            return (0.0, 0.0)
        
        return (dx / mag, dy / mag)
    
    def get_terrain_cost(
        self, 
        lat: float, 
        lon: float,
        direction: Tuple[float, float]
    ) -> float:
        """
        Calculate movement cost based on terrain.
        
        Args:
            lat, lon: Current position
            direction: (dx, dy) movement direction
        
        Returns:
            Cost multiplier (1.0 = normal, >1 = harder, <1 = easier)
        """
        slope = self.slope_at_point(lat, lon)
        
        if slope is None:
            return 1.0
        
        # Steep slopes are harder to traverse
        slope_degrees = math.degrees(math.atan(slope))
        
        if slope_degrees > 45:
            return 10.0  # Extremely difficult
        elif slope_degrees > 30:
            return 3.0  # Very difficult
        elif slope_degrees > 20:
            return 1.5  # Moderate
        else:
            return 1.0  # Normal
    
    def elevation_grid_latlon(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get lat/lon coordinate grids for the elevation data.
        
        Returns:
            (lat_grid, lon_grid) as 2D arrays
        """
        west, south, east, north = self._bounds
        rows, cols = self._shape
        
        lons = np.linspace(west, east, cols)
        lats = np.linspace(north, south, rows)  # Note: north to south
        
        lon_grid, lat_grid = np.meshgrid(lons, lats)
        return lat_grid, lon_grid
