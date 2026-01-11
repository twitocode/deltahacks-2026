"""
OpenStreetMap Feature Loader Module.

Fetches spatial features (trails, rivers, roads, cliffs) from Overpass API
and rasterizes them to grids for use in simulation.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any
import hashlib
import json

import numpy as np
import httpx
from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union

from app.config import get_settings
from app.utils.logging import timed_operation

logger = logging.getLogger(__name__)


@dataclass
class FeatureMasks:
    """Boolean masks for different feature types."""
    trails: np.ndarray  # True where trails exist
    rivers: np.ndarray  # True where water exists
    roads: np.ndarray  # True where roads exist
    cliffs: np.ndarray  # True where cliffs/steep terrain exists
    shape: Tuple[int, int]
    bounds: Tuple[float, float, float, float]


@dataclass
class OSMFeatures:
    """Raw OSM feature data."""
    trails: List[List[Tuple[float, float]]] = field(default_factory=list)
    rivers: List[List[Tuple[float, float]]] = field(default_factory=list)
    roads: List[List[Tuple[float, float]]] = field(default_factory=list)
    cliffs: List[List[Tuple[float, float]]] = field(default_factory=list)


class OSMFeatureLoader:
    """
    Loader for OpenStreetMap spatial features.
    
    Queries trails, rivers, roads, and cliffs from Overpass API
    and provides rasterized grids for simulation.
    """
    
    # Overpass query template
    QUERY_TEMPLATE = """
    [out:json][timeout:30];
    (
      // Trails and paths
      way["highway"~"path|footway|track|bridleway"]({south},{west},{north},{east});
      
      // Rivers and streams
      way["waterway"~"river|stream|creek"]({south},{west},{north},{east});
      relation["waterway"~"river|stream"]({south},{west},{north},{east});
      way["natural"="water"]({south},{west},{north},{east});
      
      // Roads
      way["highway"~"primary|secondary|tertiary|residential|unclassified"]({south},{west},{north},{east});
      
      // Cliffs and rocks
      way["natural"~"cliff|bare_rock|scree"]({south},{west},{north},{east});
    );
    out body;
    >;
    out skel qt;
    """
    
    def __init__(self):
        """Initialize the OSM feature loader."""
        self.settings = get_settings()
        self._cache: Dict[str, OSMFeatures] = {}
    
    def _get_cache_key(self, bounds: Tuple[float, float, float, float]) -> str:
        """Generate cache key for bounds."""
        return hashlib.md5(str(bounds).encode()).hexdigest()
    
    @timed_operation("fetch_osm_features")
    async def fetch_features(
        self, 
        bounds: Tuple[float, float, float, float]
    ) -> OSMFeatures:
        """
        Fetch OSM features for a bounding box.
        
        Args:
            bounds: (west, south, east, north) in degrees
        
        Returns:
            OSMFeatures with trails, rivers, roads, cliffs
        """
        cache_key = self._get_cache_key(bounds)
        if cache_key in self._cache:
            logger.debug(f"Cache hit for OSM features: {cache_key[:8]}")
            return self._cache[cache_key]
        
        west, south, east, north = bounds
        
        query = self.QUERY_TEMPLATE.format(
            south=south, west=west, north=north, east=east
        )
        
        logger.info(f"Fetching OSM features for bounds: {bounds}")
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.settings.overpass_api_url,
                    data={"data": query}
                )
                response.raise_for_status()
                data = response.json()
        except Exception as e:
            logger.error(f"Error fetching OSM data: {e}")
            # Return empty features on error
            return OSMFeatures()
        
        features = self._parse_response(data)
        self._cache[cache_key] = features
        
        logger.info(
            f"Fetched {len(features.trails)} trails, "
            f"{len(features.rivers)} rivers, "
            f"{len(features.roads)} roads, "
            f"{len(features.cliffs)} cliffs"
        )
        
        return features
    
    def _parse_response(self, data: Dict[str, Any]) -> OSMFeatures:
        """Parse Overpass API response into features."""
        features = OSMFeatures()
        
        # Build node lookup
        nodes: Dict[int, Tuple[float, float]] = {}
        for element in data.get("elements", []):
            if element["type"] == "node":
                nodes[element["id"]] = (element["lon"], element["lat"])
        
        # Extract ways
        for element in data.get("elements", []):
            if element["type"] != "way":
                continue
            
            tags = element.get("tags", {})
            node_ids = element.get("nodes", [])
            
            # Get coordinates for this way
            coords = []
            for nid in node_ids:
                if nid in nodes:
                    coords.append(nodes[nid])
            
            if len(coords) < 2:
                continue
            
            # Categorize by tags
            highway = tags.get("highway", "")
            waterway = tags.get("waterway", "")
            natural = tags.get("natural", "")
            
            if highway in ["path", "footway", "track", "bridleway"]:
                features.trails.append(coords)
            elif highway in ["primary", "secondary", "tertiary", "residential", "unclassified"]:
                features.roads.append(coords)
            
            if waterway in ["river", "stream", "creek"] or natural == "water":
                features.rivers.append(coords)
            
            if natural in ["cliff", "bare_rock", "scree"]:
                features.cliffs.append(coords)
        
        return features
    
    def rasterize_features(
        self,
        features: OSMFeatures,
        shape: Tuple[int, int],
        bounds: Tuple[float, float, float, float],
        buffer_m: float = 10.0
    ) -> FeatureMasks:
        """
        Convert vector features to raster masks.
        
        Args:
            features: OSM features
            shape: (rows, cols) grid dimensions
            bounds: (west, south, east, north)
            buffer_m: Buffer around linear features in meters
        
        Returns:
            FeatureMasks with boolean grids
        """
        rows, cols = shape
        west, south, east, north = bounds
        
        # Convert buffer to degrees (approximate)
        buffer_deg = buffer_m / 111320.0
        
        # Create coordinate grids
        lons = np.linspace(west, east, cols)
        lats = np.linspace(north, south, rows)
        
        masks = FeatureMasks(
            trails=np.zeros(shape, dtype=bool),
            rivers=np.zeros(shape, dtype=bool),
            roads=np.zeros(shape, dtype=bool),
            cliffs=np.zeros(shape, dtype=bool),
            shape=shape,
            bounds=bounds
        )
        
        # Rasterize each feature type
        masks.trails = self._rasterize_lines(
            features.trails, lons, lats, buffer_deg
        )
        masks.rivers = self._rasterize_lines(
            features.rivers, lons, lats, buffer_deg * 2
        )
        masks.roads = self._rasterize_lines(
            features.roads, lons, lats, buffer_deg * 1.5
        )
        masks.cliffs = self._rasterize_lines(
            features.cliffs, lons, lats, buffer_deg
        )
        
        logger.debug(
            f"Rasterized features: "
            f"trails={masks.trails.sum()}, "
            f"rivers={masks.rivers.sum()}, "
            f"roads={masks.roads.sum()}, "
            f"cliffs={masks.cliffs.sum()} cells"
        )
        
        return masks
    
    def _rasterize_lines(
        self,
        lines: List[List[Tuple[float, float]]],
        lons: np.ndarray,
        lats: np.ndarray,
        buffer_deg: float
    ) -> np.ndarray:
        """Rasterize a list of linestrings to a grid."""
        rows = len(lats)
        cols = len(lons)
        mask = np.zeros((rows, cols), dtype=bool)
        
        if not lines:
            return mask
        
        # Create buffered geometries
        geometries = []
        for coords in lines:
            try:
                line = LineString(coords)
                buffered = line.buffer(buffer_deg)
                geometries.append(buffered)
            except Exception:
                continue
        
        if not geometries:
            return mask
        
        # Merge all geometries
        try:
            merged = unary_union(geometries)
        except Exception:
            return mask
        
        # Check each grid cell
        for i, lat in enumerate(lats):
            for j, lon in enumerate(lons):
                point = Point(lon, lat)
                if merged.contains(point) or merged.intersects(point):
                    mask[i, j] = True
        
        return mask


# Singleton instance
_osm_loader: Optional[OSMFeatureLoader] = None


def get_osm_loader() -> OSMFeatureLoader:
    """Get or create the OSM loader singleton."""
    global _osm_loader
    if _osm_loader is None:
        _osm_loader = OSMFeatureLoader()
    return _osm_loader
