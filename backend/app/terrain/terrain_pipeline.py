"""
Terrain Pipeline Module.

Handles loading DEM data for a specified area and resampling to desired resolution.
"""

import logging
from dataclasses import dataclass
from typing import Tuple, Optional

import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling, calculate_default_transform
from rasterio.crs import CRS
from rasterio.transform import from_bounds

from app.config import get_settings
from app.dem.dem_loader import get_dem_loader, MeritDEMLoader
from app.utils.logging import timed_operation

logger = logging.getLogger(__name__)


# Earth radius for distance calculations
EARTH_RADIUS_KM = 6371.0


@dataclass
class TerrainModel:
    """
    Terrain model containing elevation data and metadata.
    """
    elevation_grid: np.ndarray  # 2D array of elevation values (meters)
    center_lat: float
    center_lon: float
    radius_km: float
    resolution_m: float
    shape: Tuple[int, int]
    bounds: Tuple[float, float, float, float]  # (west, south, east, north)
    transform: rasterio.Affine
    crs: CRS


def km_to_deg_lat(km: float) -> float:
    """Convert kilometers to degrees latitude (approximately)."""
    return km / 111.32


def km_to_deg_lon(km: float, lat: float) -> float:
    """Convert kilometers to degrees longitude at given latitude."""
    return km / (111.32 * np.cos(np.radians(lat)))


def m_to_deg(m: float, lat: float) -> Tuple[float, float]:
    """Convert meters to degrees (lat, lon) at given latitude."""
    km = m / 1000.0
    return km_to_deg_lat(km), km_to_deg_lon(km, lat)


class TerrainPipeline:
    """
    Pipeline for loading and resampling terrain data.
    
    Takes a center point and radius, loads DEM data, and resamples
    to the requested grid resolution.
    """
    
    def __init__(self, dem_loader: Optional[MeritDEMLoader] = None):
        """
        Initialize the terrain pipeline.
        
        Args:
            dem_loader: Optional DEM loader instance. Defaults to global singleton.
        """
        self.dem_loader = dem_loader or get_dem_loader()
        self.settings = get_settings()
    
    def compute_bounds(
        self, 
        center_lat: float, 
        center_lon: float, 
        radius_km: float,
        buffer_factor: float = 1.1
    ) -> Tuple[float, float, float, float]:
        """
        Compute bounding box for the terrain area.
        
        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            radius_km: Radius in kilometers
            buffer_factor: Extra buffer for safety (default 10%)
        
        Returns:
            (west, south, east, north) bounds in degrees
        """
        buffered_radius = radius_km * buffer_factor
        
        delta_lat = km_to_deg_lat(buffered_radius)
        delta_lon = km_to_deg_lon(buffered_radius, center_lat)
        
        west = center_lon - delta_lon
        east = center_lon + delta_lon
        south = center_lat - delta_lat
        north = center_lat + delta_lat
        
        return (west, south, east, north)
    
    def compute_grid_shape(
        self, 
        bounds: Tuple[float, float, float, float],
        resolution_m: float,
        center_lat: float
    ) -> Tuple[int, int]:
        """
        Compute grid dimensions for the given bounds and resolution.
        
        Args:
            bounds: (west, south, east, north)
            resolution_m: Grid cell size in meters
            center_lat: Center latitude for degree conversion
        
        Returns:
            (rows, cols) grid dimensions
        """
        west, south, east, north = bounds
        
        # Convert resolution to degrees
        res_lat, res_lon = m_to_deg(resolution_m, center_lat)
        
        cols = int(np.ceil((east - west) / res_lon))
        rows = int(np.ceil((north - south) / res_lat))
        
        return (rows, cols)
    
    @timed_operation("load_terrain")
    def load_terrain(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float,
        resolution_m: Optional[float] = None
    ) -> TerrainModel:
        """
        Load and resample terrain for the specified area.
        
        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            radius_km: Search radius in kilometers
            resolution_m: Grid resolution in meters (default from config)
        
        Returns:
            TerrainModel with elevation data
        
        Raises:
            ValueError: If parameters exceed safety limits
            FileNotFoundError: If DEM tiles not available
        """
        # Apply defaults and safety limits
        if resolution_m is None:
            resolution_m = self.settings.default_grid_resolution_m
        
        if radius_km > self.settings.max_radius_km:
            raise ValueError(
                f"Radius {radius_km}km exceeds maximum {self.settings.max_radius_km}km"
            )
        
        if resolution_m < self.settings.min_grid_resolution_m:
            raise ValueError(
                f"Resolution {resolution_m}m is below minimum {self.settings.min_grid_resolution_m}m"
            )
        
        logger.info(
            f"Loading terrain: center=({center_lat:.4f}, {center_lon:.4f}), "
            f"radius={radius_km}km, resolution={resolution_m}m"
        )
        
        # Compute bounds and load DEM
        bounds = self.compute_bounds(center_lat, center_lon, radius_km)
        dem_data = self.dem_loader.get_elevation_window(bounds)
        
        # Compute target grid shape
        target_shape = self.compute_grid_shape(bounds, resolution_m, center_lat)
        
        logger.info(
            f"Source DEM shape: {dem_data.metadata.shape}, "
            f"target shape: {target_shape}"
        )
        
        # Resample to target resolution
        elevation_resampled = self._resample_dem(
            dem_data.elevation,
            dem_data.metadata.transform,
            dem_data.metadata.crs,
            bounds,
            target_shape
        )
        
        # Compute output transform
        transform = from_bounds(*bounds, target_shape[1], target_shape[0])
        
        return TerrainModel(
            elevation_grid=elevation_resampled,
            center_lat=center_lat,
            center_lon=center_lon,
            radius_km=radius_km,
            resolution_m=resolution_m,
            shape=target_shape,
            bounds=bounds,
            transform=transform,
            crs=dem_data.metadata.crs
        )
    
    def _resample_dem(
        self,
        source: np.ndarray,
        source_transform: rasterio.Affine,
        crs: CRS,
        bounds: Tuple[float, float, float, float],
        target_shape: Tuple[int, int]
    ) -> np.ndarray:
        """
        Resample DEM to target shape using bilinear interpolation.
        
        Args:
            source: Source elevation array
            source_transform: Source affine transform
            crs: Coordinate reference system
            bounds: Target bounds
            target_shape: (rows, cols) target dimensions
        
        Returns:
            Resampled elevation array
        """
        rows, cols = target_shape
        target_transform = from_bounds(*bounds, cols, rows)
        
        destination = np.zeros(target_shape, dtype=np.float32)
        
        reproject(
            source=source.astype(np.float32),
            destination=destination,
            src_transform=source_transform,
            src_crs=crs,
            dst_transform=target_transform,
            dst_crs=crs,
            resampling=Resampling.bilinear
        )
        
        logger.debug(f"Resampled DEM from {source.shape} to {target_shape}")
        return destination


# Singleton instance
_terrain_pipeline: Optional[TerrainPipeline] = None


def get_terrain_pipeline() -> TerrainPipeline:
    """Get or create the terrain pipeline singleton."""
    global _terrain_pipeline
    if _terrain_pipeline is None:
        _terrain_pipeline = TerrainPipeline()
    return _terrain_pipeline
