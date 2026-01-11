"""
MERIT DEM Loader Module.

Single-tile constraint: All searches must fit within one 1x1 degree tile.
Features:
- In-memory LRU cache for O(1) lookups after first load
- Auto-download from NASA SRTM COG on first request
- Session-based tile tracking for cleanup on shutdown
"""

import atexit
import logging
from functools import lru_cache
from pathlib import Path
from typing import Optional, Tuple, List, NamedTuple, Dict, Set
import math
import tempfile
import shutil

import numpy as np
import rasterio
from rasterio.windows import from_bounds
from rasterio.crs import CRS

from app.config import get_settings

logger = logging.getLogger(__name__)

# NASA SRTM Global COG (Cloud Optimized GeoTIFF) - ~30m resolution
SRTM_COG_URL = "https://data.naturalcapitalalliance.stanford.edu/download/global/nasa-srtm-v3-1s/srtm-v3-1s.tif"

# Single-tile constraint: max radius that fits in one tile at ~50° latitude
# At 50°N: 1 degree lon ≈ 70km, 1 degree lat ≈ 111km
# To stay within one tile, max radius ≈ 35km (half the tile width)
MAX_SINGLE_TILE_RADIUS_KM = 35.0

# LRU cache size (number of tiles to keep in memory)
LRU_CACHE_SIZE = 4


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


class CachedTile(NamedTuple):
    """Cached tile data."""
    data: np.ndarray
    transform: rasterio.Affine
    crs: CRS
    bounds: Tuple[float, float, float, float]


class MeritDEMLoader:
    """
    DEM loader with single-tile constraint and in-memory caching.
    
    - Enforces that all queries fit within ONE 1x1 degree tile
    - LRU cache for O(1) lookups after first load
    - Auto-downloads tiles from NASA SRTM COG
    - Tracks session tiles for cleanup on shutdown
    """
    
    def __init__(
        self, 
        data_dir: Optional[Path] = None, 
        auto_download: bool = True,
        cleanup_on_exit: bool = True
    ):
        """
        Initialize the DEM loader.
        
        Args:
            data_dir: Path to tile cache directory
            auto_download: Auto-download missing tiles
            cleanup_on_exit: Delete session tiles on shutdown
        """
        settings = get_settings()
        self.data_dir = Path(data_dir) if data_dir else settings.dem_data_path
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.auto_download = auto_download
        self.cleanup_on_exit = cleanup_on_exit
        
        # In-memory LRU cache: (lat, lon) -> CachedTile
        self._memory_cache: Dict[Tuple[int, int], CachedTile] = {}
        self._cache_order: List[Tuple[int, int]] = []  # LRU order
        
        # Track tiles downloaded this session (for cleanup)
        self._session_tiles: Set[Path] = set()
        
        # Register cleanup on exit
        if cleanup_on_exit:
            atexit.register(self._cleanup_session_tiles)
        
        logger.info(f"MeritDEMLoader initialized: {self.data_dir}")
        logger.info(f"  auto_download={auto_download}, cleanup_on_exit={cleanup_on_exit}")
    
    def _get_tile_name(self, lat: int, lon: int) -> str:
        """Get tile filename."""
        return f"merit_{lat}_{lon}.tif"
    
    def _get_tile_path(self, lat: int, lon: int) -> Path:
        """Get full path to a tile file."""
        return self.data_dir / self._get_tile_name(lat, lon)
    
    def get_tile_for_point(self, lat: float, lon: float) -> Tuple[int, int]:
        """Get the tile coordinates containing a point."""
        return (math.floor(lat), math.floor(lon))
    
    def get_tile_bounds(self, lat: int, lon: int) -> Tuple[float, float, float, float]:
        """Get bounds for a tile: (west, south, east, north)."""
        return (float(lon), float(lat), float(lon + 1), float(lat + 1))
    
    def validate_single_tile(
        self, 
        center_lat: float, 
        center_lon: float, 
        radius_km: float
    ) -> Tuple[int, int]:
        """
        Validate that the search fits in one tile.
        
        Returns:
            (lat, lon) tile coordinates
        
        Raises:
            ValueError: If search spans multiple tiles
        """
        # Calculate bounds
        delta_lat = radius_km / 111.0
        delta_lon = radius_km / (111.0 * abs(math.cos(math.radians(center_lat))))
        
        south = center_lat - delta_lat
        north = center_lat + delta_lat
        west = center_lon - delta_lon
        east = center_lon + delta_lon
        
        # Check tile coverage
        lat_min = math.floor(south)
        lat_max = math.floor(north)
        lon_min = math.floor(west)
        lon_max = math.floor(east)
        
        if lat_min != lat_max or lon_min != lon_max:
            # Calculate max safe radius
            center_tile_lat = math.floor(center_lat)
            center_tile_lon = math.floor(center_lon)
            
            # Distance to nearest tile edge
            dist_to_south = (center_lat - center_tile_lat) * 111.0
            dist_to_north = (center_tile_lat + 1 - center_lat) * 111.0
            cos_lat = abs(math.cos(math.radians(center_lat)))
            dist_to_west = (center_lon - center_tile_lon) * 111.0 * cos_lat
            dist_to_east = (center_tile_lon + 1 - center_lon) * 111.0 * cos_lat
            
            max_safe_radius = min(dist_to_south, dist_to_north, dist_to_west, dist_to_east)
            
            raise ValueError(
                f"Search radius {radius_km}km spans multiple tiles. "
                f"Max radius for this location: {max_safe_radius:.1f}km"
            )
        
        return (lat_min, lon_min)
    
    def _get_from_memory_cache(self, lat: int, lon: int) -> Optional[CachedTile]:
        """Get tile from in-memory LRU cache."""
        key = (lat, lon)
        if key in self._memory_cache:
            # Move to end (most recently used)
            self._cache_order.remove(key)
            self._cache_order.append(key)
            logger.debug(f"Memory cache hit: tile ({lat}, {lon})")
            return self._memory_cache[key]
        return None
    
    def _add_to_memory_cache(self, lat: int, lon: int, tile: CachedTile):
        """Add tile to in-memory LRU cache."""
        key = (lat, lon)
        
        # Evict oldest if at capacity
        while len(self._cache_order) >= LRU_CACHE_SIZE:
            oldest_key = self._cache_order.pop(0)
            del self._memory_cache[oldest_key]
            logger.debug(f"Evicted tile from cache: {oldest_key}")
        
        self._memory_cache[key] = tile
        self._cache_order.append(key)
        logger.debug(f"Added tile to memory cache: ({lat}, {lon})")
    
    def _download_tile(self, lat: int, lon: int) -> Path:
        """Download tile from NASA SRTM COG."""
        output_path = self._get_tile_path(lat, lon)
        
        if output_path.exists():
            logger.debug(f"Tile exists on disk: {output_path.name}")
            return output_path
        
        logger.info(f"Downloading tile: {self._get_tile_name(lat, lon)}...")
        
        try:
            with rasterio.open(SRTM_COG_URL) as src:
                tile_bounds = (lon, lat, lon + 1, lat + 1)
                window = from_bounds(*tile_bounds, src.transform)
                data = src.read(1, window=window)
                win_transform = src.window_transform(window)
                
                if data.size == 0:
                    raise ValueError(f"No data for tile ({lat}, {lon})")
                
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
                
                # Track for session cleanup
                self._session_tiles.add(output_path)
                
                logger.info(f"Downloaded: {output_path.name} ({data.shape})")
                return output_path
                
        except Exception as e:
            logger.error(f"Failed to download tile ({lat}, {lon}): {e}")
            if output_path.exists():
                output_path.unlink()
            raise
    
    def load_tile(self, lat: int, lon: int) -> CachedTile:
        """
        Load a tile, using cache or downloading if needed.
        
        O(1) lookup for cached tiles.
        """
        # Check memory cache first
        cached = self._get_from_memory_cache(lat, lon)
        if cached:
            return cached
        
        # Get/download tile file
        if self.auto_download:
            tile_path = self._download_tile(lat, lon)
        else:
            tile_path = self._get_tile_path(lat, lon)
            if not tile_path.exists():
                raise FileNotFoundError(f"Tile {tile_path.name} not found")
        
        # Load into memory
        with rasterio.open(tile_path) as src:
            data = src.read(1)
            tile = CachedTile(
                data=data,
                transform=src.transform,
                crs=src.crs,
                bounds=self.get_tile_bounds(lat, lon)
            )
        
        # Cache in memory
        self._add_to_memory_cache(lat, lon, tile)
        
        return tile
    
    def get_elevation_for_search(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float
    ) -> DEMData:
        """
        Get elevation data for a search area.
        
        Enforces single-tile constraint.
        """
        # Validate single tile
        tile_lat, tile_lon = self.validate_single_tile(center_lat, center_lon, radius_km)
        
        # Load tile (from cache or download)
        tile = self.load_tile(tile_lat, tile_lon)
        
        # Calculate actual bounds
        delta_lat = radius_km / 111.0
        delta_lon = radius_km / (111.0 * abs(math.cos(math.radians(center_lat))))
        
        bounds = (
            center_lon - delta_lon,
            center_lat - delta_lat,
            center_lon + delta_lon,
            center_lat + delta_lat
        )
        
        # Extract window from cached tile
        window = from_bounds(*bounds, tile.transform)
        
        # Convert to integer indices
        row_start = max(0, int(window.row_off))
        row_end = min(tile.data.shape[0], int(window.row_off + window.height))
        col_start = max(0, int(window.col_off))
        col_end = min(tile.data.shape[1], int(window.col_off + window.width))
        
        elevation = tile.data[row_start:row_end, col_start:col_end].copy()
        
        # Calculate window transform
        from rasterio.transform import Affine
        win_transform = Affine(
            tile.transform.a,
            tile.transform.b,
            tile.transform.c + col_start * tile.transform.a,
            tile.transform.d,
            tile.transform.e,
            tile.transform.f + row_start * tile.transform.e
        )
        
        metadata = DEMMetadata(
            crs=tile.crs,
            bounds=bounds,
            transform=win_transform,
            shape=elevation.shape,
            nodata=-9999.0
        )
        
        return DEMData(elevation=elevation, metadata=metadata)
    
    def get_elevation_at_point(self, lat: float, lon: float) -> Optional[float]:
        """Get elevation at a single point. O(1) for cached tiles."""
        try:
            tile_lat, tile_lon = self.get_tile_for_point(lat, lon)
            tile = self.load_tile(tile_lat, tile_lon)
            
            row, col = rasterio.transform.rowcol(tile.transform, lon, lat)
            
            if 0 <= row < tile.data.shape[0] and 0 <= col < tile.data.shape[1]:
                value = float(tile.data[row, col])
                if value != -9999.0 and value > -500:
                    return value
            return None
            
        except Exception as e:
            logger.error(f"Error getting elevation at ({lat}, {lon}): {e}")
            return None
    
    # Legacy compatibility methods
    def get_elevation_window(self, bounds: Tuple[float, float, float, float]) -> DEMData:
        """Legacy method - load DEM for bounds."""
        west, south, east, north = bounds
        center_lat = (south + north) / 2
        center_lon = (west + east) / 2
        
        # Approximate radius from bounds
        lat_span = (north - south) * 111.0 / 2
        lon_span = (east - west) * 111.0 * abs(math.cos(math.radians(center_lat))) / 2
        radius_km = max(lat_span, lon_span)
        
        return self.get_elevation_for_search(center_lat, center_lon, radius_km)
    
    def load_merged_dem(
        self, 
        bounds: Tuple[float, float, float, float]
    ) -> Tuple[np.ndarray, rasterio.Affine, CRS]:
        """Legacy method."""
        dem_data = self.get_elevation_window(bounds)
        return dem_data.elevation, dem_data.metadata.transform, dem_data.metadata.crs
    
    def list_cached_tiles(self) -> List[str]:
        """List all locally cached tile files."""
        return [f.name for f in self.data_dir.glob("merit_*.tif")]
    
    def list_memory_cache(self) -> List[str]:
        """List tiles currently in memory cache."""
        return [f"merit_{lat}_{lon}.tif" for lat, lon in self._cache_order]
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        return {
            "memory_cache_size": len(self._memory_cache),
            "memory_cache_max": LRU_CACHE_SIZE,
            "disk_tiles": len(self.list_cached_tiles()),
            "session_tiles": len(self._session_tiles),
            "memory_tiles": self.list_memory_cache()
        }
    
    def clear_cache(self):
        """Clear both memory and disk cache."""
        self._memory_cache.clear()
        self._cache_order.clear()
        for f in self.data_dir.glob("merit_*.tif"):
            f.unlink()
        self._session_tiles.clear()
        logger.info("Cleared all DEM caches")
    
    def _cleanup_session_tiles(self):
        """Cleanup tiles downloaded this session."""
        if not self.cleanup_on_exit:
            return
        
        count = 0
        for tile_path in self._session_tiles:
            try:
                if tile_path.exists():
                    tile_path.unlink()
                    count += 1
            except Exception as e:
                logger.warning(f"Failed to cleanup {tile_path}: {e}")
        
        if count > 0:
            logger.info(f"Cleaned up {count} session tiles")
    
    def preload_tile(self, lat: int, lon: int) -> bool:
        """
        Pre-download and cache a tile.
        
        Useful for developers to pre-populate cache.
        """
        try:
            self.load_tile(lat, lon)
            return True
        except Exception as e:
            logger.error(f"Failed to preload tile ({lat}, {lon}): {e}")
            return False


# Singleton instance
_dem_loader: Optional[MeritDEMLoader] = None


def get_dem_loader(cleanup_on_exit: bool = False) -> MeritDEMLoader:
    """
    Get or create the DEM loader singleton.
    
    Args:
        cleanup_on_exit: If True, delete session tiles on shutdown.
                        Set to False for development to keep tiles.
    """
    global _dem_loader
    if _dem_loader is None:
        _dem_loader = MeritDEMLoader(cleanup_on_exit=cleanup_on_exit)
    return _dem_loader


def reset_dem_loader():
    """Reset the singleton (useful for testing)."""
    global _dem_loader
    _dem_loader = None
