import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class GridCoordinates:
    """Represents a cell in the grid"""
    x: int  # Grid column
    y: int  # Grid row
    latitude: float
    longitude: float
    elevation: float = 0.0


class TerrainModel:
    """Models terrain features and their impact on movement probability"""
    
    def __init__(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float,
        grid_resolution_m: float = 100.0
    ):
        """
        Initialize terrain model with a grid around the center point.
        
        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            radius_km: Search radius in kilometers
            grid_resolution_m: Size of each grid cell in meters
        """
        self.center_lat = center_lat
        self.center_lon = center_lon
        self.radius_km = radius_km
        self.grid_resolution_m = grid_resolution_m
        
        # Calculate grid dimensions
        self.grid_size = int((radius_km * 1000 * 2) / grid_resolution_m)
        
        # Initialize elevation grid (will be populated from data)
        self.elevation_grid = np.zeros((self.grid_size, self.grid_size))
        
        # Trail/road proximity grid (0 = no trail, 1 = on trail)
        self.trail_grid = np.zeros((self.grid_size, self.grid_size))
        
        # Water feature proximity grid
        self.water_grid = np.zeros((self.grid_size, self.grid_size))
        
        # Vegetation density grid (0 = clear, 1 = impassable)
        self.vegetation_grid = np.ones((self.grid_size, self.grid_size)) * 0.3  # Default moderate
        
    def lat_lon_to_grid(self, lat: float, lon: float) -> Tuple[int, int]:
        """
        Convert lat/lon to grid coordinates.
        
        Returns:
            (row, col) tuple, or None if out of bounds
        """
        # Approximate conversion (simplified, assumes small area)
        lat_per_m = 1 / 111320.0
        lon_per_m = 1 / (111320.0 * np.cos(np.deg2rad(self.center_lat)))
        
        # Calculate offset from center in meters
        lat_offset_m = (lat - self.center_lat) / lat_per_m
        lon_offset_m = (lon - self.center_lon) / lon_per_m
        
        # Convert to grid coordinates (center is at grid_size/2)
        center_idx = self.grid_size // 2
        col = int(center_idx + (lon_offset_m / self.grid_resolution_m))
        row = int(center_idx - (lat_offset_m / self.grid_resolution_m))  # Negative because lat increases upward
        
        return (row, col)
    
    def grid_to_lat_lon(self, row: int, col: int) -> Tuple[float, float]:
        """Convert grid coordinates to lat/lon"""
        lat_per_m = 1 / 111320.0
        lon_per_m = 1 / (111320.0 * np.cos(np.deg2rad(self.center_lat)))
        
        center_idx = self.grid_size // 2
        
        # Calculate offset in meters
        lon_offset_m = (col - center_idx) * self.grid_resolution_m
        lat_offset_m = -(row - center_idx) * self.grid_resolution_m
        
        lat = self.center_lat + (lat_offset_m * lat_per_m)
        lon = self.center_lon + (lon_offset_m * lon_per_m)
        
        return (lat, lon)
    
    def is_valid_cell(self, row: int, col: int) -> bool:
        """Check if grid cell is within bounds"""
        return 0 <= row < self.grid_size and 0 <= col < self.grid_size
    
    def calculate_slope(self, row: int, col: int) -> float:
        """
        Calculate slope at a grid cell in degrees.
        Positive = uphill, negative = downhill
        
        Uses the elevation gradient to approximate slope.
        """
        if not self.is_valid_cell(row, col):
            return 0.0
        
        # Get neighboring cells
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if self.is_valid_cell(nr, nc):
                neighbors.append(self.elevation_grid[nr, nc])
        
        if not neighbors:
            return 0.0
        
        # Calculate average elevation change
        current_elevation = self.elevation_grid[row, col]
        avg_neighbor_elevation = np.mean(neighbors)
        elevation_change = avg_neighbor_elevation - current_elevation
        
        # Convert to slope (rise over run)
        slope_radians = np.arctan(elevation_change / self.grid_resolution_m)
        return np.rad2deg(slope_radians)
    
    def get_trail_attraction(self, row: int, col: int, search_radius: int = 5) -> float:
        """
        Calculate trail attraction factor.
        Higher values near trails/roads.
        
        Args:
            row, col: Grid coordinates
            search_radius: How many cells to search around for trails
        
        Returns:
            Attraction factor (0.0 to 1.0)
        """
        if not self.is_valid_cell(row, col):
            return 0.0
        
        # Check immediate cell
        if self.trail_grid[row, col] > 0.8:
            return 1.0
        
        # Check nearby cells for trail proximity
        max_trail_value = 0.0
        for dr in range(-search_radius, search_radius + 1):
            for dc in range(-search_radius, search_radius + 1):
                nr, nc = row + dr, col + dc
                if self.is_valid_cell(nr, nc):
                    distance = np.sqrt(dr**2 + dc**2)
                    if distance > 0:
                        # Decay with distance
                        trail_influence = self.trail_grid[nr, nc] / distance
                        max_trail_value = max(max_trail_value, trail_influence)
        
        return min(max_trail_value, 1.0)
    
    def get_water_attraction(self, row: int, col: int) -> float:
        """
        Calculate water source attraction.
        People often move toward water for survival or follow drainages.
        """
        if not self.is_valid_cell(row, col):
            return 0.0
        
        return self.water_grid[row, col]
    
    def load_elevation_data(self, elevation_data: np.ndarray):
        """Load elevation data from external source"""
        if elevation_data.shape == self.elevation_grid.shape:
            self.elevation_grid = elevation_data.copy()
        else:
            # Resize if necessary
            from scipy.ndimage import zoom
            scale_factors = (
                self.elevation_grid.shape[0] / elevation_data.shape[0],
                self.elevation_grid.shape[1] / elevation_data.shape[1]
            )
            self.elevation_grid = zoom(elevation_data, scale_factors, order=1)
    
    def load_trail_data(self, trail_data: np.ndarray):
        """Load trail/road data"""
        if trail_data.shape == self.trail_grid.shape:
            self.trail_grid = trail_data.copy()
    
    def load_water_data(self, water_data: np.ndarray):
        """Load water feature data"""
        if water_data.shape == self.water_grid.shape:
            self.water_grid = water_data.copy()
