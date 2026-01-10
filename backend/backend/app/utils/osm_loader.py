"""
OpenStreetMap data loader for trail and road networks.

Loads and processes OSM data for:
- Trails (paths, footways, tracks)
- Roads (highways)
- Water features (rivers, lakes)
"""

import json
import os
import numpy as np
from typing import List, Tuple, Optional, Dict
import httpx


class OSMLoader:
    """Load and process OpenStreetMap data"""
    
    def __init__(self, data_dir: str = "data/osm"):
        self.data_dir = data_dir
        self.trails = []
        self.roads = []
        self.water_features = []
        self._use_networkx = self._check_networkx()
    
    def _check_networkx(self) -> bool:
        """Check if NetworkX is available"""
        try:
            import networkx
            return True
        except ImportError:
            return False
    
    def load_from_json(self, json_filename: str):
        """
        Load OSM data from a JSON file (Overpass API format).
        
        Args:
            json_filename: Name of JSON file in data_dir
        """
        file_path = os.path.join(self.data_dir, json_filename)
        
        if not os.path.exists(file_path):
            # File doesn't exist, return without loading
            return self
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Parse elements
        for element in data.get('elements', []):
            if element['type'] == 'way':
                self._parse_way(element)
        
        return self
    
    def _parse_way(self, way: Dict):
        """Parse a way element and categorize it"""
        tags = way.get('tags', {})
        geometry = way.get('geometry', [])
        
        if not geometry:
            return
        
        # Extract coordinates
        coords = [(node['lat'], node['lon']) for node in geometry]
        
        # Categorize by type
        highway = tags.get('highway', '')
        waterway = tags.get('waterway', '')
        natural = tags.get('natural', '')
        
        if highway in ['path', 'footway', 'track', 'bridleway']:
            self.trails.append({
                'coords': coords,
                'type': highway,
                'name': tags.get('name', 'Unnamed trail')
            })
        elif highway and highway not in ['path', 'footway', 'track', 'bridleway']:
            self.roads.append({
                'coords': coords,
                'type': highway,
                'name': tags.get('name', 'Unnamed road')
            })
        elif waterway or natural == 'water':
            self.water_features.append({
                'coords': coords,
                'type': waterway or 'water',
                'name': tags.get('name', 'Unnamed water')
            })
    
    async def fetch_osm_data(
        self,
        min_lat: float,
        min_lon: float,
        max_lat: float,
        max_lon: float,
        timeout: float = 30.0
    ) -> Optional[Dict]:
        """
        Fetch OSM data from Overpass API for a bounding box.
        
        Args:
            min_lat, min_lon, max_lat, max_lon: Bounding box coordinates
            timeout: Request timeout in seconds
            
        Returns:
            OSM data as dictionary
        """
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        # Build Overpass QL query
        query = f"""
        [out:json][timeout:{int(timeout)}];
        (
          way["highway"~"path|footway|track|bridleway"]({min_lat},{min_lon},{max_lat},{max_lon});
          way["highway"]({min_lat},{min_lon},{max_lat},{max_lon});
          way["waterway"]({min_lat},{min_lon},{max_lat},{max_lon});
          way["natural"="water"]({min_lat},{min_lon},{max_lat},{max_lon});
        );
        out geom;
        """
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    overpass_url,
                    data=query,
                    timeout=timeout
                )
                return response.json()
            except Exception as e:
                print(f"Failed to fetch OSM data: {e}")
                return None
    
    def get_nearest_trail_distance(
        self,
        lat: float,
        lon: float
    ) -> float:
        """
        Calculate distance to nearest trail in meters.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Distance in meters (0 if no trails loaded)
        """
        if not self.trails:
            return float('inf')
        
        min_distance = float('inf')
        
        for trail in self.trails:
            for trail_lat, trail_lon in trail['coords']:
                distance = self._haversine_distance(
                    lat, lon, trail_lat, trail_lon
                )
                min_distance = min(min_distance, distance)
        
        return min_distance
    
    def get_nearest_road_distance(
        self,
        lat: float,
        lon: float
    ) -> float:
        """
        Calculate distance to nearest road in meters.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Distance in meters (0 if no roads loaded)
        """
        if not self.roads:
            return float('inf')
        
        min_distance = float('inf')
        
        for road in self.roads:
            for road_lat, road_lon in road['coords']:
                distance = self._haversine_distance(
                    lat, lon, road_lat, road_lon
                )
                min_distance = min(min_distance, distance)
        
        return min_distance
    
    def get_nearest_water_distance(
        self,
        lat: float,
        lon: float
    ) -> float:
        """
        Calculate distance to nearest water feature in meters.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Distance in meters (infinity if no water loaded)
        """
        if not self.water_features:
            return float('inf')
        
        min_distance = float('inf')
        
        for water in self.water_features:
            for water_lat, water_lon in water['coords']:
                distance = self._haversine_distance(
                    lat, lon, water_lat, water_lon
                )
                min_distance = min(min_distance, distance)
        
        return min_distance
    
    def _haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate haversine distance between two points in meters.
        
        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates
            
        Returns:
            Distance in meters
        """
        R = 6371000  # Earth radius in meters
        
        lat1_rad = np.radians(lat1)
        lat2_rad = np.radians(lat2)
        delta_lat = np.radians(lat2 - lat1)
        delta_lon = np.radians(lon2 - lon1)
        
        a = (np.sin(delta_lat / 2) ** 2 +
             np.cos(lat1_rad) * np.cos(lat2_rad) *
             np.sin(delta_lon / 2) ** 2)
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        
        return R * c
    
    def build_network_graph(self):
        """
        Build a NetworkX graph from trail/road data.
        
        Requires NetworkX to be installed.
        """
        if not self._use_networkx:
            raise ImportError(
                "NetworkX is required for graph building. "
                "Install with: pip install networkx"
            )
        
        import networkx as nx
        
        G = nx.Graph()
        
        # Add trails as edges
        for trail in self.trails:
            coords = trail['coords']
            for i in range(len(coords) - 1):
                start = coords[i]
                end = coords[i + 1]
                
                # Calculate edge length
                length = self._haversine_distance(
                    start[0], start[1], end[0], end[1]
                )
                
                G.add_edge(start, end, length=length, type='trail')
        
        # Add roads as edges
        for road in self.roads:
            coords = road['coords']
            for i in range(len(coords) - 1):
                start = coords[i]
                end = coords[i + 1]
                
                length = self._haversine_distance(
                    start[0], start[1], end[0], end[1]
                )
                
                G.add_edge(start, end, length=length, type='road')
        
        return G
    
    def get_trail_density_grid(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float,
        grid_size: int
    ) -> np.ndarray:
        """
        Calculate trail density for each grid cell.
        
        Returns a grid where each cell value represents trail proximity
        (higher = closer to trails).
        """
        # Calculate bounds
        lat_offset = radius_km / 111.0
        lon_offset = radius_km / (111.0 * np.cos(np.radians(center_lat)))
        
        min_lat = center_lat - lat_offset
        max_lat = center_lat + lat_offset
        min_lon = center_lon - lon_offset
        max_lon = center_lon + lon_offset
        
        # Create grid
        lats = np.linspace(max_lat, min_lat, grid_size)
        lons = np.linspace(min_lon, max_lon, grid_size)
        
        density_grid = np.zeros((grid_size, grid_size))
        
        for i, lat in enumerate(lats):
            for j, lon in enumerate(lons):
                trail_dist = self.get_nearest_trail_distance(lat, lon)
                road_dist = self.get_nearest_road_distance(lat, lon)
                
                # Closer = higher density value
                # Use exponential decay: max at 0m, ~0 at 500m
                min_dist = min(trail_dist, road_dist)
                density_grid[i, j] = np.exp(-min_dist / 200.0)
        
        return density_grid
