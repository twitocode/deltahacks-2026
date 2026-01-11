"""
SAR Simulator Module.

Monte Carlo random-walk simulation for predicting missing person locations.
"""

import logging
import math
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict, Any
from enum import Enum
import concurrent.futures

import numpy as np
from tqdm import tqdm

from app.config import get_settings
from app.terrain.terrain_pipeline import TerrainModel, get_terrain_pipeline
from app.terrain.terrain_sampler import TerrainSampler
from app.terrain.osm_features import FeatureMasks, OSMFeatures, get_osm_loader
from app.simulation.models import HikerProfile, WeatherConditions, TimeSlice
from app.simulation.weather import get_weather_service
from app.utils.logging import timed_operation, measure_time

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
    id: int  # Unique identifier
    lat: float
    lon: float
    elevation: float
    strategy: Strategy
    heading: float  # Direction in radians (0 = North, clockwise)
    steps_taken: int = 0
    energy: float = 1.0  # 0-1, decreases over time
    is_active: bool = True


class AgentTracker:
    """
    Tracks a single agent throughout the simulation for debugging.
    Logs all decisions, movement, and energy changes.
    Auto-switches to another active agent when tracked agent stops.
    """
    
    def __init__(self, agents: List[Agent], enabled: bool = True):
        self.enabled = enabled
        self.agents = agents
        self.tracked_id: Optional[int] = None
        self.log_lines: List[str] = []
        
        if enabled and agents:
            self._select_random_agent()
    
    def _select_random_agent(self):
        """Select a random active agent to track."""
        active = [a for a in self.agents if a.is_active]
        if active:
            import random
            agent = random.choice(active)
            self.tracked_id = agent.id
            self._log(f"🎯 Now tracking Agent #{agent.id} (Strategy: {agent.strategy.value})")
            self._log(f"   Start: ({agent.lat:.5f}, {agent.lon:.5f}) | Elev: {agent.elevation:.0f}m | Energy: {agent.energy:.0%}")
        else:
            self.tracked_id = None
            self._log("⚠️ No active agents to track")
    
    def _log(self, msg: str):
        """Add to log and print."""
        self.log_lines.append(msg)
        logger.info(f"[TRACKER] {msg}")
    
    def _get_tracked_agent(self) -> Optional[Agent]:
        """Get the currently tracked agent."""
        if self.tracked_id is None:
            return None
        for a in self.agents:
            if a.id == self.tracked_id:
                return a
        return None
    
    def log_step_start(self, step: int):
        """Log at the start of a simulation step."""
        if not self.enabled:
            return
        
        agent = self._get_tracked_agent()
        if agent is None or not agent.is_active:
            # Switch to another agent
            self._log(f"❌ Agent #{self.tracked_id} stopped - switching...")
            self._select_random_agent()
            agent = self._get_tracked_agent()
        
        if agent:
            self._log(f"━━━ Step {step} | Agent #{agent.id} ━━━")
    
    def log_decision(
        self,
        agent_id: int,
        decision_type: str,
        details: str
    ):
        """Log a decision made by the tracked agent."""
        if not self.enabled or agent_id != self.tracked_id:
            return
        self._log(f"   📍 {decision_type}: {details}")
    
    def log_movement(
        self,
        agent_id: int,
        old_lat: float,
        old_lon: float,
        new_lat: float,
        new_lon: float,
        distance_m: float,
        direction: str,
        speed_mps: float
    ):
        """Log movement of the tracked agent."""
        if not self.enabled or agent_id != self.tracked_id:
            return
        self._log(f"   🚶 Moved {direction}: {distance_m:.1f}m @ {speed_mps:.2f} m/s")
        self._log(f"      ({old_lat:.5f}, {old_lon:.5f}) → ({new_lat:.5f}, {new_lon:.5f})")
    
    def log_energy(self, agent_id: int, old_energy: float, new_energy: float, reason: str):
        """Log energy change for tracked agent."""
        if not self.enabled or agent_id != self.tracked_id:
            return
        
        change = new_energy - old_energy
        bar = self._energy_bar(new_energy)
        self._log(f"   ⚡ Energy: {bar} {new_energy:.0%} ({change:+.1%}) [{reason}]")
    
    def log_stop(self, agent_id: int, reason: str):
        """Log when an agent stops."""
        if not self.enabled or agent_id != self.tracked_id:
            return
        self._log(f"   ⛔ STOPPED: {reason}")
    
    def _energy_bar(self, energy: float) -> str:
        """Create visual energy bar."""
        filled = int(energy * 10)
        empty = 10 - filled
        return f"[{'█' * filled}{'░' * empty}]"
    
    def get_summary(self) -> str:
        """Get summary of tracked agent's journey."""
        agent = self._get_tracked_agent()
        if not agent:
            return "No agent tracked"
        
        return (
            f"Agent #{agent.id}: {agent.steps_taken} steps, "
            f"Energy: {agent.energy:.0%}, Active: {agent.is_active}"
        )



@dataclass
class SimulationResult:
    """Result of a simulation run."""
    time_slices: List[TimeSlice]
    final_positions: List[Tuple[float, float]]
    center_lat: float
    center_lon: float
    radius_km: float


# --- Standalone functions for multiprocessing ---

def _latlon_to_index(
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
    row: int,
    col: int,
    shape: Tuple[int, int]
) -> bool:
    """Check if grid indices are valid."""
    return 0 <= row < shape[0] and 0 <= col < shape[1]

def _calculate_direction_weights(
    agent: Agent,
    sampler: TerrainSampler,
    features: FeatureMasks,
    profile: HikerProfile,
    terrain: TerrainModel,
    directions: List[Tuple[int, int]]
) -> List[float]:
    """Calculate movement probability weights for each direction."""
    weights = []
    
    # Grid position for feature lookup
    row, col = _latlon_to_index(
        agent.lat, agent.lon, terrain
    )
    
    for dx, dy in directions:
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
        check_row, check_col = _latlon_to_index(
            check_lat, check_lon, terrain
        )
        
        if _is_valid_index(check_row, check_col, features.shape):
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

def step_single_agent_pure(
    agent: Agent,
    sampler: TerrainSampler,
    features: FeatureMasks,
    profile: HikerProfile,
    weather: WeatherConditions,
    terrain: TerrainModel,
    timestep_seconds: int = 900,
    center_lat: float = 0.0,
    center_lon: float = 0.0,
    radius_km: float = 10.0
) -> Tuple[Agent, List[Dict[str, Any]]]:
    """
    Move a single agent based on terrain, features, and profile.
    Returns: (Updated Agent, List of log events)
    """
    logs = []
    
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
    
    # Increment step counter
    agent.steps_taken += 1
    
    # Time-based stop probability (ISRID data)
    # 25% stop > 1hr (4 steps), 50% > 5hr (20 steps), 95% > 24hr (96 steps)
    if agent.steps_taken > 4:
        if agent.steps_taken > 96:
            stop_prob = 0.05
        elif agent.steps_taken > 20:
            stop_prob = 0.02
        else:
            stop_prob = 0.005
        
        if random.random() < stop_prob:
            agent.is_active = False
            logs.append({"type": "stop", "reason": f"ISRID User fatigue stop (prob={stop_prob:.1%})"})
            return agent, logs
    
    # Strategy: Staying Put
    if agent.strategy == Strategy.STAYING_PUT:
        if random.random() < 0.99:
            logs.append({"type": "decision", "decision_type": "WAIT", "details": "Staying put (99% chance)"})
            return agent, logs
    
    # Effective speed calculation
    profile_speed = profile.speed_factor
    weather_penalty = weather.movement_penalty
    
    # Direction selection based on strategy
    dx, dy = 0.0, 0.0
    
    if agent.strategy == Strategy.DIRECTION_TRAVELING:
        # Use persistent heading with small variance
        heading_variance = 0.15  # ~8 degrees
        actual_heading = agent.heading + random.gauss(0, heading_variance)
        dx = math.sin(actual_heading)
        dy = math.cos(actual_heading)
        logs.append({
            "type": "decision", 
            "decision_type": "MOVE", 
            "details": f"Direction Traveling (Goal: {math.degrees(agent.heading):.0f}°, Actual: {math.degrees(actual_heading):.0f}°)"
        })
    else:
        # Other strategies use weighted random direction
        weights = _calculate_direction_weights(
            agent, sampler, features, profile, terrain, DIRECTIONS
        )
        
        total_weight = sum(weights)
        if total_weight < 0.001:
            agent.is_active = False
            logs.append({"type": "stop", "reason": "Trapped (0 valid moves)"})
            return agent, logs
            
        normalized = [w / total_weight for w in weights]
        direction_idx = random.choices(range(8), weights=normalized)[0]
        dx, dy = DIRECTIONS[direction_idx]
        
        # Add randomness based on profile & Strategy
        randomness = profile.direction_randomness
        if agent.strategy == Strategy.RANDOM_WALKING:
            randomness = 1.0
                
        dx += random.gauss(0, randomness * 0.3)
        dy += random.gauss(0, randomness * 0.3)
        
        cardinal = DIRECTIONS[direction_idx]
        logs.append({
            "type": "decision",
            "decision_type": "MOVE",
            "details": f"Weighted Choice (Idx: {direction_idx}, Base: {cardinal})"
        })
    
    # Normalize direction
    mag = math.sqrt(dx**2 + dy**2)
    if mag > 0:
        dx /= mag
        dy /= mag
        
    # Determine target LatLon
    # Tobler's Function
    lookahead_dist = 20.0 # meters
    lookahead_lat = agent.lat + dy * (lookahead_dist / 111320.0)
    lookahead_lon = agent.lon + dx * (lookahead_dist / (111320.0 * math.cos(math.radians(agent.lat))))
    
    slope = sampler.slope(agent.lat, agent.lon, lookahead_lat, lookahead_lon) or 0.0
    
    tobler_speed_kmh = 6 * math.exp(-3.5 * abs(slope + 0.05))
    tobler_speed_mps = tobler_speed_kmh / 3.6
    
    # Apply factors
    final_speed = tobler_speed_mps * (profile_speed / 1.317)
    final_speed *= (1.0 - weather_penalty)
    final_speed *= agent.energy
    
    distance_m = final_speed * timestep_seconds
    
    distance_lat = distance_m / 111320.0
    distance_lon = distance_m / (111320.0 * math.cos(math.radians(agent.lat)))
    
    new_lat = agent.lat + dy * distance_lat
    new_lon = agent.lon + dx * distance_lon
    
    # Check bounds (terrain bounds)
    west, south, east, north = terrain.bounds
    if not (south <= new_lat <= north and west <= new_lon <= east):
        agent.is_active = False
        logs.append({"type": "stop", "reason": "Left simulation bounds"})
        return agent, logs
    
    # Check distance from center (search radius)
    # Using Haversine formula approximation
    dlat = math.radians(new_lat - center_lat)
    dlon = math.radians(new_lon - center_lon)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(center_lat)) * math.cos(math.radians(new_lat)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance_from_center_km = 6371.0 * c  # Earth radius in km
    
    if distance_from_center_km > radius_km:
        agent.is_active = False
        logs.append({"type": "stop", "reason": f"Exceeded search radius ({distance_from_center_km:.2f}km > {radius_km}km)"})
        return agent, logs
    
    # Update agent position
    new_elevation = sampler.elevation(new_lat, new_lon)
    if new_elevation is None:
            agent.is_active = False
            logs.append({"type": "stop", "reason": "Moved to invalid terrain (No elevation)"})
            return agent, logs

    old_lat = agent.lat
    old_lon = agent.lon
    old_energy = agent.energy

    agent.lat = new_lat
    agent.lon = new_lon
    agent.elevation = new_elevation
    
    # Log successful move
    logs.append({
        "type": "movement",
        "old_lat": old_lat,
        "old_lon": old_lon,
        "new_lat": new_lat,
        "new_lon": new_lon,
        "distance_m": distance_m,
        "direction": f"{dx:.2f},{dy:.2f}",
        "speed_mps": final_speed
    })
    
    # Energy and Fatigue (Simple model)
    energy_loss = 0.005 # Base metabolic cost
    if slope > 0:
            energy_loss += slope * 0.05 # Uphill cost
    
    agent.energy = max(0.1, agent.energy - energy_loss)
    logs.append({
        "type": "energy",
        "old_energy": old_energy,
        "new_energy": agent.energy,
        "reason": f"Walk cost + Slope {slope:.2f}"
    })
    
    return agent, logs


class SARSimulator:
    """
    Monte Carlo simulator for SAR probability prediction.
    
    Simulates multiple agents (possible person trajectories) using
    random walks influenced by terrain, weather, and profile.
    """
    
    # Movement constants
    BASE_SPEED_MPS = 1.0  # Base walking speed m/s
    TIMESTEP_SECONDS = 900  # 15 minutes
    
    def __init__(self):
        """Initialize the simulator."""
        self.settings = get_settings()
        self.terrain_pipeline = get_terrain_pipeline()
        self.osm_loader = get_osm_loader()
        self.weather_service = get_weather_service()
    
    @timed_operation("run_simulation_total")
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
        with measure_time("load_terrain"):
            terrain = self.terrain_pipeline.load_terrain(
                center_lat, center_lon, radius_km
            )
        sampler = TerrainSampler(terrain)
        
        # Load OSM features
        with measure_time("fetch_osm_features"):
            osm_features = await self.osm_loader.fetch_features(terrain.bounds)
            feature_masks = self.osm_loader.rasterize_features(
                osm_features, terrain.shape, terrain.bounds
            )
        
        # Get weather conditions
        with measure_time("get_weather"):
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
        
        # Total simulation: from t=0 to t+8 hours (480 minutes max)
        # We generate heatmaps at 15-minute intervals
        total_minutes = min(elapsed_minutes + (8 * 60), 480)  # Cap at 8 hours
        num_steps = total_minutes // self.settings.timestep_minutes
        
        logger.info(
            f"Simulating {num_steps} timesteps "
            f"({total_minutes} minutes total, {self.settings.num_agents} agents)"
        )
        
        # Initialize agents at last known location
        with measure_time("initialize_agents"):
            agents = self._initialize_agents(
                center_lat, center_lon, sampler, self.settings.num_agents
            )
        
        # Initialize agent tracker for debugging (set enabled=False to disable)
        tracker = AgentTracker(agents, enabled=True)
        
        # Run simulation
        time_slices = []
        
        with measure_time("simulation_loop"):
            for step in tqdm(range(num_steps), desc="Simulating", unit="step"):
                time_offset = step * self.settings.timestep_minutes
                
                # Log step start for tracked agent
                tracker.log_step_start(step)
                
                # Update agent positions
                agents = await self._step_agents(
                    agents, sampler, feature_masks, profile, weather, terrain, tracker,
                    center_lat, center_lon, radius_km
                )
                
                # Update tracker's reference to agents list since we might have replaced it
                tracker.agents = agents
                
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
                id=len(agents),  # Unique ID
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
    
    async def _step_agents(
        self,
        agents: List[Agent],
        sampler: TerrainSampler,
        features: FeatureMasks,
        profile: HikerProfile,
        weather: WeatherConditions,
        terrain: TerrainModel,
        tracker: AgentTracker,
        center_lat: float,
        center_lon: float,
        radius_km: float
    ) -> List[Agent]:
        """
        Advance all agents by one timestep.
        Uses parallel processing if enabled in settings.
        """
        active_agents = [a for a in agents if a.is_active]
        inactive_agents = [a for a in agents if not a.is_active]
        
        if not active_agents:
            return agents
            
        settings = get_settings()
        
        # 1. Identify tracked agent to run locally
        tracked_agent = None
        other_agents = []
        
        if tracker.enabled and tracker.tracked_id is not None:
            for agent in active_agents:
                if agent.id == tracker.tracked_id:
                    tracked_agent = agent
                else:
                    other_agents.append(agent)
            
            # If tracked agent was not found in active list (maybe it stopped), 
            # then all active agents are "others"
            if tracked_agent is None:
                other_agents = active_agents
        else:
            other_agents = active_agents
            
        updated_agents = []
        
        # 2. Run tracked agent locally (synchronously) to handle logging
        if tracked_agent:
            updated_one, logs = step_single_agent_pure(
                tracked_agent, sampler, features, profile, weather, terrain, self.TIMESTEP_SECONDS,
                center_lat, center_lon, radius_km
            )
            updated_agents.append(updated_one)
            
            # Replay logs to tracker
            for log in logs:
                if log["type"] == "decision":
                    tracker.log_decision(updated_one.id, log["decision_type"], log["details"])
                elif log["type"] == "movement":
                    tracker.log_movement(
                        updated_one.id, 
                        log["old_lat"], log["old_lon"], 
                        log["new_lat"], log["new_lon"],
                        log["distance_m"], log["direction"], log["speed_mps"]
                    )
                elif log["type"] == "energy":
                    tracker.log_energy(
                        updated_one.id, log["old_energy"], log["new_energy"], log["reason"]
                    )
                elif log["type"] == "stop":
                    tracker.log_stop(updated_one.id, log["reason"])

        # 3. Run other agents (Parallel or Serial)
        if other_agents:
            if settings.parallel_agents and settings.max_workers > 1:
                # Parallel Execution
                chunk_size = max(1, len(other_agents) // (settings.max_workers * 4))
                
                with concurrent.futures.ProcessPoolExecutor(max_workers=settings.max_workers) as executor:
                    # Submit tasks
                    futures = [
                        executor.submit(
                            step_single_agent_pure,
                            agent, sampler, features, profile, weather, terrain, self.TIMESTEP_SECONDS,
                            center_lat, center_lon, radius_km
                        ) 
                        for agent in other_agents
                    ]
                    
                    # Collect results
                    for future in concurrent.futures.as_completed(futures):
                        try:
                            updated_agent, _ = future.result() # Ignore logs from parallel agents
                            updated_agents.append(updated_agent)
                        except Exception as e:
                            logger.error(f"Error in parallel agent step: {e}")
                            # If individual agent fails, we might lose it or should return original?
                            # For now, let's just log. ideally keep old state?
                            pass
            else:
                # Serial Execution
                for agent in other_agents:
                    updated_agent, _ = step_single_agent_pure(
                        agent, sampler, features, profile, weather, terrain, self.TIMESTEP_SECONDS,
                        center_lat, center_lon, radius_km
                    )
                    updated_agents.append(updated_agent)
        
        # Recombine all agents
        # Sort by ID to maintain consistent order if needed, or just extend
        all_agents = updated_agents + inactive_agents
        all_agents.sort(key=lambda a: a.id)
        
        return all_agents

    def _latlon_to_index(
        self,
        lat: float,
        lon: float,
        terrain: TerrainModel
    ) -> Tuple[int, int]:
        """Convert lat/lon to grid indices."""
        return _latlon_to_index(lat, lon, terrain)
    
    def _is_valid_index(
        self,
        row: int,
        col: int,
        shape: Tuple[int, int]
    ) -> bool:
        """Check if grid indices are valid."""
        return _is_valid_index(row, col, shape)
    
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
