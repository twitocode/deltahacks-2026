"""
MERIT DEM Loader Module.

Handles loading DEM .tif tiles with automatic downloading and local caching.
Tile naming convention: merit_{lat}_{lon}.tif where lat/lon are integer floor values.

Auto-downloads missing tiles from NASA SRTM global COG on first request,
then caches locally for fast subsequent lookups.
"""

import logging
from pathlib import Path
from typing import Optional, Tuple, List, NamedTuple, Dict, Any
import math

import numpy as np
import rasterio
from rasterio.merge import merge
from rasterio.windows import from_bounds
from rasterio.crs import CRS
from rasterio.io import MemoryFile

from app.config import get_settings

logger = logging.getLogger(__name__)

# NASA SRTM Global COG (Cloud Optimized GeoTIFF) - ~30m resolution
SRTM_COG_URL = "https://data.naturalcapitalalliance.stanford.edu/download/global/nasa-srtm-v3-1s/srtm-v3-1s.tif"

# Maximum tiles to download per request (safety limit)
MAX_TILES_PER_REQUEST = 9  # 3x3 grid = 9 tiles max (~333km x 333km at equator)

# Maximum search radius in km (enforced to prevent memory issues)
MAX_RADIUS_KM = 5.0


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
    Loader for DEM tiles with auto-download and caching.
    
    Automatically downloads 1x1 degree tiles from NASA SRTM COG when needed,
    caches them locally, and merges to cover requested areas.
    """
    
    def __init__(self, data_dir: Optional[Path] = None, auto_download: bool = True):
        """
        Initialize the DEM loader.
        
        Args:
            data_dir: Path to directory for DEM tiles cache.
                     Defaults to config.dem_data_path.
            auto_download: Whether to auto-download missing tiles (default True)
        """
        settings = get_settings()
        self.data_dir = Path(data_dir) if data_dir else settings.dem_data_path
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.auto_download = auto_download
        self._tile_cache: Dict[str, Path] = {}  # Track downloaded tiles
        logger.info(f"MeritDEMLoader initialized: {self.data_dir} (auto_download={auto_download})")
    
    def _get_tile_name(self, lat: int, lon: int) -> str:
        """Get tile filename for given lat/lon integers."""
        return f"merit_{lat}_{lon}.tif"
    
    def _get_tile_path(self, lat: int, lon: int) -> Path:
        """Get full path to a tile file."""
        return self.data_dir / self._get_tile_name(lat, lon)
    
    def _get_tiles_for_bounds(
        self, 
        bounds: Tuple[float, float, float, float]
    ) -> List[Tuple[int, int]]:
        """
        Identify which tiles are needed to cover the requested bounds.
        
        Args:
            bounds: (west, south, east, north) in degrees
        
        Returns:
            List of (lat, lon) integer tuples for needed tiles
        """
        west, south, east, north = bounds
        
        lat_min = math.floor(south)
        lat_max = math.floor(north)
        lon_min = math.floor(west)
        lon_max = math.floor(east)
        
        tiles = []
        for lat in range(lat_min, lat_max + 1):
            for lon in range(lon_min, lon_max + 1):
                tiles.append((lat, lon))
        
        # Safety check
        if len(tiles) > MAX_TILES_PER_REQUEST:
            raise ValueError(
                f"Request requires {len(tiles)} tiles, max is {MAX_TILES_PER_REQUEST}. "
                f"Reduce search radius (max {MAX_RADIUS_KM}km)."
            )
        
        return tiles
    
    def _ensure_tile_exists(self, lat: int, lon: int) -> Path:
        """
        Ensure a tile exists locally, downloading if needed.
        
        Args:
            lat: Integer latitude (floor value)
            lon: Integer longitude (floor value)
        
        Returns:
            Path to local tile file
        
        Raises:
            FileNotFoundError: If tile unavailable and auto_download is False
        """
        tile_path = self._get_tile_path(lat, lon)
        
        # Already cached locally
        if tile_path.exists():
            logger.debug(f"Using cached tile: {tile_path.name}")
            return tile_path
        
        # Need to download
        if not self.auto_download:
            raise FileNotFoundError(
                f"Tile {tile_path.name} not found and auto_download is disabled"
            )
        
        logger.info(f"Downloading tile: {self._get_tile_name(lat, lon)}")
        self._download_tile(lat, lon, tile_path)
        return tile_path
    
    def _download_tile(self, lat: int, lon: int, output_path: Path):
        """
        Download a 1x1 degree tile from NASA SRTM COG.
        
        Uses HTTP range requests to fetch only the needed portion.
        """
        try:
            with rasterio.open(SRTM_COG_URL) as src:
                # Define tile bounds (1 degree square)
                tile_bounds = (lon, lat, lon + 1, lat + 1)
                
                # Get window from bounds
                window = from_bounds(*tile_bounds, src.transform)
                
                # Read data for this window
                data = src.read(1, window=window)
                win_transform = src.window_transform(window)
                
                if data.size == 0:
                    raise ValueError(f"No data returned for tile ({lat}, {lon})")
                
                # Save as local GeoTIFF with compression
                profile = src.profile.copy()
                profile.update({
                    'driver': 'GTiff',
                    'height': data.shape[0],
                    'width': data.shape[1],
                    'transform': win_transform,
                    'compress': 'lzw',
                    'tiled': True,
                    'blockxsize': 256,
                    'blockysize': 256
                })
                
                with rasterio.open(output_path, 'w', **profile) as dst:
                    dst.write(data, 1)
                
                logger.info(f"Downloaded and cached: {output_path.name} ({data.shape})")
                
        except Exception as e:
            logger.error(f"Failed to download tile ({lat}, {lon}): {e}")
            # Clean up partial file
            if output_path.exists():
                output_path.unlink()
            raise
    
    def get_tiles_for_bounds(
        self, 
        bounds: Tuple[float, float, float, float]
    ) -> List[Path]:
        """
        Get all tile files needed for bounds, downloading if necessary.
        
        Args:
            bounds: (west, south, east, north) in degrees
        
        Returns:
            List of paths to local tile files
        """
        tile_coords = self._get_tiles_for_bounds(bounds)
        
        tile_paths = []
        for lat, lon in tile_coords:
            path = self._ensure_tile_exists(lat, lon)
            tile_paths.append(path)
        
        logger.info(f"Ready: {len(tile_paths)} tiles for bounds {bounds}")
        return tile_paths
    
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
            nodata=-9999.0
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
            buffer_deg: Small buffer for bounds query
        
        Returns:
            Elevation in meters, or None if unavailable
        """
        try:
            tile_path = self._ensure_tile_exists(math.floor(lat), math.floor(lon))
            
            with rasterio.open(tile_path) as src:
                row, col = src.index(lon, lat)
                
                # Bounds check
                if row < 0 or col < 0 or row >= src.height or col >= src.width:
                    return None
                
                elevation = src.read(1, window=((row, row+1), (col, col+1)))
                value = float(elevation[0, 0])
                
                if value == -9999.0 or value < -500:  # nodata or invalid
                    return None
                return value
                
        except Exception as e:
            logger.error(f"Error getting elevation at ({lat}, {lon}): {e}")
            return None
    
    def list_cached_tiles(self) -> List[str]:
        """List all locally cached tiles."""
        return [f.name for f in self.data_dir.glob("merit_*.tif")]
    
    def clear_cache(self):
        """Clear all cached tiles."""
        for f in self.data_dir.glob("merit_*.tif"):
            f.unlink()
        logger.info("Cleared DEM tile cache")


# Singleton instance for reuse
_dem_loader: Optional[MeritDEMLoader] = None


def get_dem_loader() -> MeritDEMLoader:
    """Get or create the DEM loader singleton."""
    global _dem_loader
    if _dem_loader is None:
        _dem_loader = MeritDEMLoader()
    return _dem_loader
