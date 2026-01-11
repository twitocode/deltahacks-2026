"""
SAR Simulator Module.

Monte Carlo random-walk simulation for predicting missing person locations.
"""

import logging
import math
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

import numpy as np

from app.config import get_settings
from app.terrain.terrain_pipeline import TerrainModel, get_terrain_pipeline
from app.terrain.terrain_sampler import TerrainSampler
from app.terrain.osm_features import FeatureMasks, OSMFeatures, get_osm_loader
from app.simulation.models import HikerProfile, WeatherConditions, TimeSlice
from app.simulation.weather import get_weather_service

logger = logging.getLogger(__name__)


@dataclass
class Agent:
    """A simulated agent representing possible person location."""
    lat: float
    lon: float
    elevation: float
    energy: float = 1.0  # 0-1, decreases over time
    is_active: bool = True


@dataclass
class SimulationResult:
    """Result of a simulation run."""
    time_slices: List[TimeSlice]
    final_positions: List[Tuple[float, float]]
    center_lat: float
    center_lon: float
    radius_km: float


class SARSimulator:
    """
    Monte Carlo simulator for SAR probability prediction.
    
    Simulates multiple agents (possible person trajectories) using
    random walks influenced by terrain, weather, and profile.
    """
    
    # Movement constants
    BASE_SPEED_MPS = 1.0  # Base walking speed m/s
    TIMESTEP_SECONDS = 900  # 15 minutes
    
    # Movement direction weights
    DIRECTIONS = [
        (0, 1),    # North
        (1, 1),    # NE
        (1, 0),    # East
        (1, -1),   # SE
        (0, -1),   # South
        (-1, -1),  # SW
        (-1, 0),   # West
        (-1, 1),   # NW
    ]
    
    def __init__(self):
        """Initialize the simulator."""
        self.settings = get_settings()
        self.terrain_pipeline = get_terrain_pipeline()
        self.osm_loader = get_osm_loader()
        self.weather_service = get_weather_service()
    
    async def run_simulation(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float,
        profile: HikerProfile,
        time_last_seen: Optional[datetime] = None,
        current_time: Optional[datetime] = None,
        grid_size: int = 50
    ) -> SimulationResult:
        """
        Run Monte Carlo simulation for SAR prediction.
        
        Args:
            center_lat: Last known latitude
            center_lon: Last known longitude
            radius_km: Search radius
            profile: Hiker profile
            time_last_seen: When person was last seen
            current_time: Current time (for elapsed calculation)
            grid_size: Output grid size (default 50x50)
        
        Returns:
            SimulationResult with time series of probability distributions
        """
        logger.info(
            f"Starting SAR simulation: center=({center_lat:.4f}, {center_lon:.4f}), "
            f"radius={radius_km}km, agents={self.settings.num_agents}"
        )
        
        # Load terrain
        terrain = self.terrain_pipeline.load_terrain(
            center_lat, center_lon, radius_km
        )
        sampler = TerrainSampler(terrain)
        
        # Load OSM features
        osm_features = await self.osm_loader.fetch_features(terrain.bounds)
        feature_masks = self.osm_loader.rasterize_features(
            osm_features, terrain.shape, terrain.bounds
        )
        
        # Get weather conditions
        elevation = sampler.elevation(center_lat, center_lon) or 1000.0
        weather = await self.weather_service.get_conditions(
            center_lat, center_lon, current_time, elevation
        )
        
        # Calculate simulation duration
        if time_last_seen and current_time:
            elapsed = current_time - time_last_seen
            elapsed_minutes = int(elapsed.total_seconds() / 60)
        else:
            elapsed_minutes = 0
        
        # Total simulation: from t=0 to t+12 hours
        # We generate heatmaps at 15-minute intervals
        total_minutes = elapsed_minutes + (12 * 60)  # +12 hours ahead
        num_steps = total_minutes // self.settings.timestep_minutes
        
        logger.info(
            f"Simulating {num_steps} timesteps "
            f"({total_minutes} minutes total, {self.settings.num_agents} agents)"
        )
        
        # Initialize agents at last known location
        agents = self._initialize_agents(
            center_lat, center_lon, sampler, self.settings.num_agents
        )
        
        # Run simulation
        time_slices = []
        
        for step in range(num_steps):
            time_offset = step * self.settings.timestep_minutes
            
            # Update agent positions
            self._step_agents(
                agents, sampler, feature_masks, profile, weather, terrain
            )
            
            # Generate heatmap for this timestep
            heatmap = self._agents_to_heatmap(agents, terrain)
            grid = self._agents_to_grid(agents, terrain, grid_size)
            
            time_slices.append(TimeSlice(
                time_offset_minutes=time_offset,
                points=heatmap,
                grid=grid
            ))
            
            # Log progress periodically
            if step % 10 == 0:
                active = sum(1 for a in agents if a.is_active)
                logger.debug(f"Step {step}/{num_steps}: {active} active agents")
        
        # Get final positions
        final_positions = [
            (a.lat, a.lon) for a in agents if a.is_active
        ]
        
        logger.info(
            f"Simulation complete: {len(time_slices)} time slices, "
            f"{len(final_positions)} active agents remaining"
        )
        
        return SimulationResult(
            time_slices=time_slices,
            final_positions=final_positions,
            center_lat=center_lat,
            center_lon=center_lon,
            radius_km=radius_km
        )
    
    def _initialize_agents(
        self,
        lat: float,
        lon: float,
        sampler: TerrainSampler,
        num_agents: int
    ) -> List[Agent]:
        """Initialize agents at the starting location with small spread."""
        agents = []
        
        # Small initial spread (100m)
        spread = 0.001  # ~100m in degrees
        
        for _ in range(num_agents):
            agent_lat = lat + random.gauss(0, spread / 3)
            agent_lon = lon + random.gauss(0, spread / 3)
            
            elevation = sampler.elevation(agent_lat, agent_lon) or 0.0
            
            agents.append(Agent(
                lat=agent_lat,
                lon=agent_lon,
                elevation=elevation,
                energy=1.0,
                is_active=True
            ))
        
        return agents
    
    def _step_agents(
        self,
        agents: List[Agent],
        sampler: TerrainSampler,
        features: FeatureMasks,
        profile: HikerProfile,
        weather: WeatherConditions,
        terrain: TerrainModel
    ) -> None:
        """Advance all agents by one timestep."""
        for agent in agents:
            if not agent.is_active:
                continue
            
            self._step_single_agent(
                agent, sampler, features, profile, weather, terrain
            )
    
    def _step_single_agent(
        self,
        agent: Agent,
        sampler: TerrainSampler,
        features: FeatureMasks,
        profile: HikerProfile,
        weather: WeatherConditions,
        terrain: TerrainModel
    ) -> None:
        """Move a single agent based on terrain, features, and profile."""
        # Calculate effective speed
        speed = self.BASE_SPEED_MPS * profile.speed_factor
        speed *= (1.0 - weather.movement_penalty)
        speed *= agent.energy
        
        # Distance traveled in this timestep (meters)
        distance_m = speed * self.TIMESTEP_SECONDS
        
        # Convert to degrees (approximate)
        distance_lat = distance_m / 111320.0
        distance_lon = distance_m / (111320.0 * math.cos(math.radians(agent.lat)))
        
        # Calculate direction weights
        weights = self._calculate_direction_weights(
            agent, sampler, features, profile, terrain
        )
        
        # Choose direction probabilistically
        total_weight = sum(weights)
        if total_weight < 0.001:
            # Agent is stuck
            agent.is_active = False
            return
        
        normalized = [w / total_weight for w in weights]
        direction_idx = random.choices(range(8), weights=normalized)[0]
        dx, dy = self.DIRECTIONS[direction_idx]
        
        # Add randomness based on profile
        randomness = profile.direction_randomness
        dx += random.gauss(0, randomness * 0.3)
        dy += random.gauss(0, randomness * 0.3)
        
        # Normalize
        mag = math.sqrt(dx**2 + dy**2)
        if mag > 0:
            dx /= mag
            dy /= mag
        
        # Move agent
        new_lat = agent.lat + dy * distance_lat
        new_lon = agent.lon + dx * distance_lon
        
        # Check bounds
        west, south, east, north = terrain.bounds
        if not (south <= new_lat <= north and west <= new_lon <= east):
            agent.is_active = False
            return
        
        # Check terrain passability
        new_elevation = sampler.elevation(new_lat, new_lon)
        if new_elevation is None:
            agent.is_active = False
            return
        
        # Check for impassable terrain (very steep or cliffs)
        slope = sampler.slope(agent.lat, agent.lon, new_lat, new_lon)
        if slope is not None and abs(slope) > 0.7:  # > 35 degrees
            # 50% chance to not move if very steep
            if random.random() < 0.5:
                return
        
        # Update agent position
        agent.lat = new_lat
        agent.lon = new_lon
        agent.elevation = new_elevation
        
        # Decrease energy over time
        energy_loss = 0.01  # Base loss per step
        if new_elevation > agent.elevation:  # Going uphill
            energy_loss += 0.01
        if weather.temperature_c < 0 or weather.temperature_c > 30:
            energy_loss += 0.005
        
        agent.energy = max(0.1, agent.energy - energy_loss)
    
    def _calculate_direction_weights(
        self,
        agent: Agent,
        sampler: TerrainSampler,
        features: FeatureMasks,
        profile: HikerProfile,
        terrain: TerrainModel
    ) -> List[float]:
        """Calculate movement probability weights for each direction."""
        weights = []
        
        # Grid position for feature lookup
        row, col = self._latlon_to_index(
            agent.lat, agent.lon, terrain
        )
        
        for dx, dy in self.DIRECTIONS:
            weight = 1.0
            
            # Small movement for direction checking
            check_lat = agent.lat + dy * 0.0005
            check_lon = agent.lon + dx * 0.0005
            
            # Terrain slope influence
            slope = sampler.slope(agent.lat, agent.lon, check_lat, check_lon)
            if slope is not None:
                if slope > 0.3:  # Steep uphill
                    weight *= 0.3 if profile.skill_level < 3 else 0.5
                elif slope > 0.1:  # Moderate uphill
                    weight *= 0.6
                elif slope < -0.1:  # Downhill - generally preferred
                    weight *= 1.2
            
            # Trail preference
            check_row, check_col = self._latlon_to_index(
                check_lat, check_lon, terrain
            )
            if self._is_valid_index(check_row, check_col, features.shape):
                # Strong preference for trails
                if features.trails[check_row, check_col]:
                    weight *= 2.0 * profile.trail_preference + 1.0
                
                # Prefer roads when lost
                if features.roads[check_row, check_col]:
                    weight *= 1.5
                
                # Avoid water
                if features.rivers[check_row, check_col]:
                    weight *= 0.1
                
                # Avoid cliffs
                if features.cliffs[check_row, check_col]:
                    weight *= 0.05
            
            # Low energy agents prefer staying put or downhill
            if agent.energy < 0.3:
                if slope is not None and slope > 0:
                    weight *= 0.2  # Very unlikely to go uphill when exhausted
            
            weights.append(max(0.01, weight))
        
        return weights
    
    def _latlon_to_index(
        self,
        lat: float,
        lon: float,
        terrain: TerrainModel
    ) -> Tuple[int, int]:
        """Convert lat/lon to grid indices."""
        west, south, east, north = terrain.bounds
        rows, cols = terrain.shape
        
        col = int((lon - west) / (east - west) * cols)
        row = int((north - lat) / (north - south) * rows)
        
        return row, col
    
    def _is_valid_index(
        self,
        row: int,
        col: int,
        shape: Tuple[int, int]
    ) -> bool:
        """Check if grid indices are valid."""
        return 0 <= row < shape[0] and 0 <= col < shape[1]
    
    def _agents_to_heatmap(
        self,
        agents: List[Agent],
        terrain: TerrainModel
    ) -> List[Tuple[float, float, float]]:
        """
        Convert agent positions to heatmap points.
        
        Returns list of (lat, lon, probability) tuples.
        """
        # Create density grid
        rows, cols = terrain.shape
        density = np.zeros((rows, cols), dtype=np.float32)
        
        active_count = 0
        for agent in agents:
            if not agent.is_active:
                continue
            
            row, col = self._latlon_to_index(agent.lat, agent.lon, terrain)
            if self._is_valid_index(row, col, terrain.shape):
                density[row, col] += 1
                active_count += 1
        
        if active_count == 0:
            return []
        
        # Normalize to probabilities
        density /= active_count
        
        # Apply Gaussian smoothing for visualization
        from scipy.ndimage import gaussian_filter
        density = gaussian_filter(density, sigma=1.5)
        
        # Convert to list of points
        west, south, east, north = terrain.bounds
        lon_per_col = (east - west) / cols
        lat_per_row = (north - south) / rows
        
        points = []
        threshold = 0.0001  # Minimum probability to include
        
        for r in range(rows):
            for c in range(cols):
                if density[r, c] > threshold:
                    lat = north - (r + 0.5) * lat_per_row
                    lon = west + (c + 0.5) * lon_per_col
                    points.append((lat, lon, float(density[r, c])))
        
        # Normalize intensities to 0-1 range
        if points:
            max_intensity = max(p[2] for p in points)
            if max_intensity > 0:
                points = [(p[0], p[1], p[2] / max_intensity) for p in points]
        
        return points
    
    def _agents_to_grid(
        self,
        agents: List[Agent],
        terrain: TerrainModel,
        grid_size: int = 50
    ) -> List[List[float]]:
        """
        Convert agent positions to a fixed-size probability grid.
        
        Returns grid_size x grid_size matrix of probabilities (0-1).
        Row 0 is North, Row (grid_size-1) is South.
        Col 0 is West, Col (grid_size-1) is East.
        """
        from scipy.ndimage import gaussian_filter
        
        # Create density grid at output resolution
        density = np.zeros((grid_size, grid_size), dtype=np.float32)
        
        west, south, east, north = terrain.bounds
        
        active_count = 0
        for agent in agents:
            if not agent.is_active:
                continue
            
            # Map agent position to grid cell
            col = int((agent.lon - west) / (east - west) * grid_size)
            row = int((north - agent.lat) / (north - south) * grid_size)
            
            # Clamp to valid range
            col = max(0, min(col, grid_size - 1))
            row = max(0, min(row, grid_size - 1))
            
            density[row, col] += 1
            active_count += 1
        
        if active_count == 0:
            return [[0.0] * grid_size for _ in range(grid_size)]
        
        # Normalize to probabilities
        density /= active_count
        
        # Apply Gaussian smoothing
        density = gaussian_filter(density, sigma=1.5)
        
        # Normalize to 0-1 range
        max_val = density.max()
        if max_val > 0:
            density /= max_val
        
        # Convert to nested list
        return density.tolist()


# Singleton instance
_simulator: Optional[SARSimulator] = None


def get_simulator() -> SARSimulator:
    """Get or create the simulator singleton."""
    global _simulator
    if _simulator is None:
        _simulator = SARSimulator()
    return _simulator
