"""
MERIT DEM Loader Module.

Handles loading and merging of pre-downloaded MERIT DEM .tif tiles.
Tile naming convention: merit_{lat}_{lon}.tif where lat/lon are integer floor values.
"""

import logging
from pathlib import Path
from typing import Optional, Tuple, List, NamedTuple
import math

import numpy as np
import rasterio
from rasterio.merge import merge
from rasterio.windows import from_bounds
from rasterio.crs import CRS

from app.config import get_settings

logger = logging.getLogger(__name__)


class DEMMetadata(NamedTuple):
    """Metadata for a loaded DEM window."""
    crs: CRS
    bounds: Tuple[float, float, float, float]  # (west, south, east, north)
    transform: rasterio.Affine
    shape: Tuple[int, int]  # (rows, cols)
    nodata: Optional[float]


class DEMData(NamedTuple):
    """DEM elevation data with metadata."""
    elevation: np.ndarray  # 2D array of elevation values
    metadata: DEMMetadata


class MeritDEMLoader:
    """
    Loader for MERIT DEM tiles.
    
    Loads pre-downloaded DEM .tif tiles from a local directory,
    merges multiple tiles to cover requested areas, and returns
    elevation grids with metadata.
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize the DEM loader.
        
        Args:
            data_dir: Path to directory containing MERIT DEM tiles.
                     Defaults to config.dem_data_path.
        """
        settings = get_settings()
        self.data_dir = data_dir or settings.dem_data_path
        self._tile_cache: dict[str, rasterio.DatasetReader] = {}
        logger.info(f"MeritDEMLoader initialized with data directory: {self.data_dir}")
    
    def _get_tile_name(self, lat: int, lon: int) -> str:
        """
        Get the tile filename for given lat/lon integers.
        
        Args:
            lat: Integer latitude (floor of actual latitude)
            lon: Integer longitude (floor of actual longitude)
        
        Returns:
            Tile filename (e.g., 'merit_51_-116.tif')
        """
        return f"merit_{lat}_{lon}.tif"
    
    def _get_tile_path(self, lat: int, lon: int) -> Path:
        """Get full path to a tile file."""
        return self.data_dir / self._get_tile_name(lat, lon)
    
    def get_tiles_for_bounds(
        self, 
        bounds: Tuple[float, float, float, float]
    ) -> List[Path]:
        """
        Identify which tiles are needed to cover the requested bounds.
        
        Args:
            bounds: (west, south, east, north) in degrees
        
        Returns:
            List of paths to required tile files
        """
        west, south, east, north = bounds
        
        # Get integer ranges for tiles
        lat_min = math.floor(south)
        lat_max = math.floor(north)
        lon_min = math.floor(west)
        lon_max = math.floor(east)
        
        tiles = []
        missing = []
        
        for lat in range(lat_min, lat_max + 1):
            for lon in range(lon_min, lon_max + 1):
                tile_path = self._get_tile_path(lat, lon)
                if tile_path.exists():
                    tiles.append(tile_path)
                    logger.debug(f"Found tile: {tile_path.name}")
                else:
                    missing.append(self._get_tile_name(lat, lon))
        
        if missing:
            logger.warning(f"Missing DEM tiles: {missing}")
        
        if not tiles:
            raise FileNotFoundError(
                f"No DEM tiles found for bounds {bounds}. "
                f"Expected tiles in: {self.data_dir}"
            )
        
        logger.info(f"Found {len(tiles)} tiles for bounds {bounds}")
        return tiles
    
    def load_merged_dem(
        self, 
        bounds: Tuple[float, float, float, float]
    ) -> Tuple[np.ndarray, rasterio.Affine, CRS]:
        """
        Load and merge DEM tiles covering the requested bounds.
        
        Args:
            bounds: (west, south, east, north) in degrees
        
        Returns:
            Tuple of (elevation_array, transform, crs)
        """
        tile_paths = self.get_tiles_for_bounds(bounds)
        
        if len(tile_paths) == 1:
            # Single tile - no merge needed
            with rasterio.open(tile_paths[0]) as src:
                window = from_bounds(*bounds, src.transform)
                data = src.read(1, window=window)
                transform = src.window_transform(window)
                crs = src.crs
                logger.info(f"Loaded single tile: {tile_paths[0].name}, shape: {data.shape}")
                return data, transform, crs
        
        # Multiple tiles - merge them
        datasets = []
        try:
            for path in tile_paths:
                datasets.append(rasterio.open(path))
            
            merged, merged_transform = merge(datasets, bounds=bounds)
            crs = datasets[0].crs
            
            # merge() returns 3D array (bands, rows, cols), take first band
            elevation = merged[0]
            logger.info(f"Merged {len(tile_paths)} tiles, shape: {elevation.shape}")
            
            return elevation, merged_transform, crs
            
        finally:
            for ds in datasets:
                ds.close()
    
    def get_elevation_window(
        self, 
        bounds: Tuple[float, float, float, float]
    ) -> DEMData:
        """
        Get elevation data for a bounding box.
        
        Args:
            bounds: (west, south, east, north) in degrees
        
        Returns:
            DEMData with elevation grid and metadata
        """
        elevation, transform, crs = self.load_merged_dem(bounds)
        
        metadata = DEMMetadata(
            crs=crs,
            bounds=bounds,
            transform=transform,
            shape=elevation.shape,
            nodata=-9999.0  # MERIT DEM nodata value
        )
        
        return DEMData(elevation=elevation, metadata=metadata)
    
    def get_elevation_at_point(
        self, 
        lat: float, 
        lon: float,
        buffer_deg: float = 0.001
    ) -> Optional[float]:
        """
        Get elevation at a single point.
        
        Args:
            lat: Latitude
            lon: Longitude
            buffer_deg: Small buffer to ensure point is within bounds
        
        Returns:
            Elevation in meters, or None if not available
        """
        bounds = (
            lon - buffer_deg,
            lat - buffer_deg,
            lon + buffer_deg,
            lat + buffer_deg
        )
        
        try:
            tile_path = self._get_tile_path(math.floor(lat), math.floor(lon))
            if not tile_path.exists():
                return None
            
            with rasterio.open(tile_path) as src:
                # Convert lat/lon to pixel coordinates
                row, col = src.index(lon, lat)
                elevation = src.read(1, window=((row, row+1), (col, col+1)))
                value = float(elevation[0, 0])
                
                if value == -9999.0:  # nodata
                    return None
                return value
                
        except Exception as e:
            logger.error(f"Error getting elevation at ({lat}, {lon}): {e}")
            return None


# Singleton instance for reuse
_dem_loader: Optional[MeritDEMLoader] = None


def get_dem_loader() -> MeritDEMLoader:
    """Get or create the DEM loader singleton."""
    global _dem_loader
    if _dem_loader is None:
        _dem_loader = MeritDEMLoader()
    return _dem_loader
