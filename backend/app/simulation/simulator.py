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
from enum import Enum

import numpy as np
from tqdm import tqdm

from app.config import get_settings
from app.terrain.terrain_pipeline import TerrainModel, get_terrain_pipeline
from app.terrain.terrain_sampler import TerrainSampler
from app.terrain.osm_features import FeatureMasks, OSMFeatures, get_osm_loader
from app.simulation.models import HikerProfile, WeatherConditions, TimeSlice
from app.simulation.weather import get_weather_service

logger = logging.getLogger(__name__)


class Strategy(str, Enum):
    """Movement strategies from ISRID data."""
    DIRECTION_TRAVELING = "DT"  # 55.9%
    ROUTE_TRAVELING = "RT"      # 37.7%
    RANDOM_WALKING = "RW"       # 5.5%
    VIEW_ENHANCING = "VE"       # 0.6%
    STAYING_PUT = "SP"          # 0.3%


@dataclass
class Agent:
    """A simulated agent representing possible person location."""
    lat: float
    lon: float
    elevation: float
    strategy: Strategy
    heading: float  # Direction in radians (0 = North, clockwise)
    steps_taken: int = 0
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
            # Strip timezone info for comparison (make both naive)
            tls = time_last_seen.replace(tzinfo=None) if time_last_seen.tzinfo else time_last_seen
            ct = current_time.replace(tzinfo=None) if current_time.tzinfo else current_time
            elapsed = ct - tls
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
        
        for step in tqdm(range(num_steps), desc="Simulating", unit="step"):
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
            
            # Assign strategy based on probabilities
            # DT: 55.9%, RT: 37.7%, RW: 5.5%, VE: 0.6%, SP: 0.3%
            r = random.random() * 100
            if r < 55.9:
                strategy = Strategy.DIRECTION_TRAVELING
            elif r < 55.9 + 37.7:
                strategy = Strategy.ROUTE_TRAVELING
            elif r < 55.9 + 37.7 + 5.5:
                strategy = Strategy.RANDOM_WALKING
            elif r < 55.9 + 37.7 + 5.5 + 0.6:
                strategy = Strategy.VIEW_ENHANCING
            else:
                strategy = Strategy.STAYING_PUT

            # Assign random heading (radians, 0=North)
            heading = random.uniform(0, 2 * math.pi)

            agents.append(Agent(
                lat=agent_lat,
                lon=agent_lon,
                elevation=elevation,
                strategy=strategy,
                heading=heading,
                steps_taken=0,
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
        
        # Increment step counter
        agent.steps_taken += 1
        
        # Time-based stop probability (ISRID data)
        # 25% stop > 1hr (4 steps), 50% > 5hr (20 steps), 95% > 24hr (96 steps)
        # We model this as a per-step probability to achieve cumulative target
        if agent.steps_taken > 4:
            # Calculate stop probability per step to reach target
            if agent.steps_taken > 96:
                stop_prob = 0.05  # Lowered from 0.15
            elif agent.steps_taken > 20:
                stop_prob = 0.02  # Lowered from 0.05
            else:
                stop_prob = 0.005  # Lowered from 0.02
            
            if random.random() < stop_prob:
                agent.is_active = False
                return
        
        # Strategy: Staying Put
        if agent.strategy == Strategy.STAYING_PUT:
            if random.random() < 0.99:
                return
        
        # Effective speed calculation
        profile_speed = profile.speed_factor
        weather_penalty = weather.movement_penalty
        
        # Direction selection based on strategy
        if agent.strategy == Strategy.DIRECTION_TRAVELING:
            # Use persistent heading with small variance
            heading_variance = 0.15  # ~8 degrees
            actual_heading = agent.heading + random.gauss(0, heading_variance)
            dx = math.sin(actual_heading)
            dy = math.cos(actual_heading)
        else:
            # Other strategies use weighted random direction
            weights = self._calculate_direction_weights(
                agent, sampler, features, profile, terrain
            )
            
            total_weight = sum(weights)
            if total_weight < 0.001:
                agent.is_active = False
                return
                
            normalized = [w / total_weight for w in weights]
            direction_idx = random.choices(range(8), weights=normalized)[0]
            dx, dy = self.DIRECTIONS[direction_idx]
            
            # Add randomness based on profile & Strategy
            randomness = profile.direction_randomness
            if agent.strategy == Strategy.RANDOM_WALKING:
                randomness = 1.0
                 
            dx += random.gauss(0, randomness * 0.3)
            dy += random.gauss(0, randomness * 0.3)
        
        # Normalize direction
        mag = math.sqrt(dx**2 + dy**2)
        if mag > 0:
            dx /= mag
            dy /= mag
            
        # Determine target LatLon
        # Calculate speed with Tobler's Function
        # We need slope in the chosen direction. To approximate, we sample a point ahead.
        lookahead_dist = 20.0 # meters
        lookahead_lat = agent.lat + dy * (lookahead_dist / 111320.0)
        lookahead_lon = agent.lon + dx * (lookahead_dist / (111320.0 * math.cos(math.radians(agent.lat))))
        
        slope = sampler.slope(agent.lat, agent.lon, lookahead_lat, lookahead_lon) or 0.0
        
        # Tobler's Hiking Function: W = 6 * exp(-3.5 * |dh/dx + 0.05|) km/h
        # dh/dx is slope (tan theta)
        tobler_speed_kmh = 6 * math.exp(-3.5 * abs(slope + 0.05))
        tobler_speed_mps = tobler_speed_kmh / 3.6
        
        # Apply factors
        final_speed = tobler_speed_mps * (profile_speed / 1.317) # Normalize profile to male base to scale Tobler
        final_speed *= (1.0 - weather_penalty)
        final_speed *= agent.energy
        
        distance_m = final_speed * self.TIMESTEP_SECONDS
        
        distance_lat = distance_m / 111320.0
        distance_lon = distance_m / (111320.0 * math.cos(math.radians(agent.lat)))
        
        new_lat = agent.lat + dy * distance_lat
        new_lon = agent.lon + dx * distance_lon
        
         # Check bounds
        west, south, east, north = terrain.bounds
        if not (south <= new_lat <= north and west <= new_lon <= east):
            agent.is_active = False
            return
        
        # Update agent position
        new_elevation = sampler.elevation(new_lat, new_lon)
        if new_elevation is None:
             agent.is_active = False
             return

        agent.lat = new_lat
        agent.lon = new_lon
        agent.elevation = new_elevation
        
        # Energy and Fatigue (Simple model)
        energy_loss = 0.005 # Base metabolic cost
        if slope > 0:
             energy_loss += slope * 0.05 # Uphill cost
        
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
            
            # Lookahead for features
            check_lat = agent.lat + dy * 0.0005 # ~50m
            check_lon = agent.lon + dx * 0.0005
            
            # 1. Slope / Signal Seeking (Uphill bias)
            # Historically downhill, BUT new data says uphill for signal
            slope = sampler.slope(agent.lat, agent.lon, check_lat, check_lon)
            if slope is not None:
                if slope > 0: # Uphill
                     if agent.strategy == Strategy.VIEW_ENHANCING:
                         weight *= 3.0 # Strong pull uphill
                     else:
                         weight *= 1.2 # General bias for signal
                else: # Downhill
                     weight *= 0.8 # Reduced bias
            
            # 2. Linear Features (Trails/Roads)
            check_row, check_col = self._latlon_to_index(
                check_lat, check_lon, terrain
            )
            
            if self._is_valid_index(check_row, check_col, features.shape):
                # Trail Attraction
                # If doing Route Traveling, very strong pull
                is_on_trail = features.trails[check_row, check_col]
                is_on_road = features.roads[check_row, check_col]
                
                if is_on_trail or is_on_road:
                    if agent.strategy == Strategy.ROUTE_TRAVELING:
                         weight *= 5.0 
                    else:
                         weight *= 2.0 # General attraction (58m rule)
                
                # Water Avoidance (unless thirsty? assume avoidance for safety)
                if features.rivers[check_row, check_col]:
                    weight *= 0.1
                
                 # Cliff Avoidance
                if features.cliffs[check_row, check_col]:
                    weight *= 0.01

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
        density = gaussian_filter(density, sigma=0.5)
        
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
        density = gaussian_filter(density, sigma=0.5)
        
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
