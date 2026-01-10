import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import uuid

from app.models.schemas import (
    PredictionRequest, PredictionResponse, TimeSnapshot, GridCell
)
from app.models.terrain_model import TerrainModel
from app.models.human_behavior import BehaviorModel, MovementStrategy


class PredictionEngine:
    """Core engine for predicting hiker location probabilities over time"""
    
    def __init__(self):
        self.behavior_model = BehaviorModel()
    
    def predict(self, request: PredictionRequest) -> PredictionResponse:
        """
        Generate probability predictions for hiker location over time.
        
        Returns snapshots every 15 minutes from time_last_seen to current + 12 hours.
        """
        # Parse time
        time_last_seen = datetime.fromisoformat(request.time_last_seen.replace('Z', '+00:00'))
        current_time = datetime.utcnow()
        
        # Calculate time range
        hours_since_last_seen = (current_time - time_last_seen).total_seconds() / 3600
        total_hours = hours_since_last_seen + 12  # Current + 12 hours prediction
        
        # Initialize terrain model
        terrain = TerrainModel(
            center_lat=request.last_known_location.latitude,
            center_lon=request.last_known_location.longitude,
            radius_km=request.search_radius_km,
            grid_resolution_m=request.grid_resolution_m
        )
        
        # TODO: Load actual terrain data
        # For now, generate synthetic elevation for testing
        terrain.elevation_grid = self._generate_synthetic_elevation(terrain.grid_size)
        
        # Initialize probability grid at LKL
        start_row, start_col = terrain.lat_lon_to_grid(
            request.last_known_location.latitude,
            request.last_known_location.longitude
        )
        
        probability_grid = np.zeros((terrain.grid_size, terrain.grid_size))
        probability_grid[start_row, start_col] = 1.0
        
        # Generate snapshots every 15 minutes (0.25 hours)
        snapshots = []
        interval_hours = 0.25
        num_intervals = int(total_hours / interval_hours)
        
        for i in range(num_intervals + 1):
            hours_elapsed = i * interval_hours
            snapshot_time = time_last_seen + timedelta(hours=hours_elapsed)
            
            # Evolve probability distribution
            if i > 0:
                probability_grid = self._evolve_probability(
                    probability_grid=probability_grid,
                    terrain=terrain,
                    subject_profile=request.subject_profile,
                    hours_elapsed=hours_elapsed,
                    interval_hours=interval_hours
                )
            
            # Create snapshot
            snapshot = self._create_snapshot(
                probability_grid=probability_grid,
                terrain=terrain,
                timestamp=snapshot_time,
                hours_elapsed=hours_elapsed
            )
            snapshots.append(snapshot)
        
        return PredictionResponse(
            request_id=str(uuid.uuid4()),
            snapshots=snapshots,
            metadata={
                "grid_size": terrain.grid_size,
                "grid_resolution_m": request.grid_resolution_m,
                "search_radius_km": request.search_radius_km,
                "total_snapshots": len(snapshots),
                "subject_age": request.subject_profile.age,
                "subject_experience": request.subject_profile.experience_level.value
            }
        )
    
    def _evolve_probability(
        self,
        probability_grid: np.ndarray,
        terrain: TerrainModel,
        subject_profile,
        hours_elapsed: float,
        interval_hours: float
    ) -> np.ndarray:
        """
        Evolve the probability distribution based on movement patterns.
        
        This is the core simulation step - the agent moves probabilistically
        based on terrain, behavior, and time elapsed.
        """
        new_grid = np.zeros_like(probability_grid)
        
        # Get movement parameters
        base_travel_rate = self.behavior_model.get_base_travel_rate(
            subject_profile.age,
            subject_profile.sex
        )
        panic_mult = self.behavior_model.get_panic_multiplier(hours_elapsed)
        movement_strategies = self.behavior_model.get_movement_strategy_weights(
            subject_profile.age,
            subject_profile.sex,
            subject_profile.experience_level,
            hours_elapsed
        )
        
        # For each cell with probability
        for row in range(probability_grid.shape[0]):
            for col in range(probability_grid.shape[1]):
                current_prob = probability_grid[row, col]
                
                if current_prob < 1e-6:  # Skip negligible probabilities
                    continue
                
                # Calculate movement from this cell
                self._distribute_probability(
                    source_row=row,
                    source_col=col,
                    source_prob=current_prob,
                    new_grid=new_grid,
                    terrain=terrain,
                    base_travel_rate=base_travel_rate * panic_mult,
                    movement_strategies=movement_strategies,
                    interval_hours=interval_hours
                )
        
        # Normalize probabilities
        total_prob = np.sum(new_grid)
        if total_prob > 0:
            new_grid /= total_prob
        
        return new_grid
    
    def _distribute_probability(
        self,
        source_row: int,
        source_col: int,
        source_prob: float,
        new_grid: np.ndarray,
        terrain: TerrainModel,
        base_travel_rate: float,
        movement_strategies: Dict[MovementStrategy, float],
        interval_hours: float
    ):
        """
        Distribute probability from a source cell to neighboring cells.
        
        This implements the agent movement logic.
        """
        # Calculate how far the subject can travel in this interval
        max_distance_m = base_travel_rate * (interval_hours / 0.25)  # base_travel_rate is per 15 min
        max_cells = int(max_distance_m / terrain.grid_resolution_m) + 1
        
        # Weights for staying put vs moving
        stay_weight = movement_strategies.get(MovementStrategy.STAYING_PUT, 0.1)
        
        # Subject might stay in current cell
        new_grid[source_row, source_col] += source_prob * stay_weight
        
        # Distribute remaining probability to reachable cells
        move_prob = source_prob * (1 - stay_weight)
        
        # Get all reachable neighboring cells
        neighbor_weights = {}
        
        for dr in range(-max_cells, max_cells + 1):
            for dc in range(-max_cells, max_cells + 1):
                if dr == 0 and dc == 0:
                    continue
                
                target_row = source_row + dr
                target_col = source_col + dc
                
                if not terrain.is_valid_cell(target_row, target_col):
                    continue
                
                # Calculate movement weight to this cell
                weight = self._calculate_movement_weight(
                    source_row=source_row,
                    source_col=source_col,
                    target_row=target_row,
                    target_col=target_col,
                    terrain=terrain,
                    movement_strategies=movement_strategies,
                    max_distance_m=max_distance_m
                )
                
                if weight > 0:
                    neighbor_weights[(target_row, target_col)] = weight
        
        # Normalize and distribute
        if neighbor_weights:
            total_weight = sum(neighbor_weights.values())
            for (target_row, target_col), weight in neighbor_weights.items():
                new_grid[target_row, target_col] += move_prob * (weight / total_weight)
        else:
            # If no valid neighbors, stay put
            new_grid[source_row, source_col] += move_prob
    
    def _calculate_movement_weight(
        self,
        source_row: int,
        source_col: int,
        target_row: int,
        target_col: int,
        terrain: TerrainModel,
        movement_strategies: Dict[MovementStrategy, float],
        max_distance_m: float
    ) -> float:
        """
        Calculate the weight/probability of moving from source to target cell.
        
        This combines:
        - Distance decay
        - Terrain factors (slope, vegetation)
        - Behavioral attraction (trails, water)
        - Movement strategy preferences
        """
        # Distance check
        dr = target_row - source_row
        dc = target_col - source_col
        distance_cells = np.sqrt(dr**2 + dc**2)
        distance_m = distance_cells * terrain.grid_resolution_m
        
        if distance_m > max_distance_m:
            return 0.0
        
        # Base weight with distance decay
        weight = np.exp(-distance_m / (max_distance_m * 0.5))
        
        # Terrain modifiers
        slope = terrain.calculate_slope(target_row, target_col)
        vegetation = terrain.vegetation_grid[target_row, target_col]
        
        # Apply slope modifier based on movement strategies
        if slope > 0:  # Uphill
            uphill_weight = movement_strategies.get(MovementStrategy.UPHILL_SEEKING, 0.1)
            weight *= (0.3 + 0.7 * uphill_weight)  # Penalty for uphill, unless seeking
        else:  # Downhill
            downhill_weight = movement_strategies.get(MovementStrategy.DOWNHILL_SEEKING, 0.1)
            weight *= (0.8 + 0.2 * downhill_weight)  # Slight bonus for downhill
        
        # Vegetation penalty
        weight *= (1.0 - 0.6 * vegetation)
        
        # Trail attraction (VERY important - most found near trails)
        trail_attraction = terrain.get_trail_attraction(target_row, target_col)
        route_weight = movement_strategies.get(MovementStrategy.ROUTE_TRAVELING, 0.2)
        weight *= (1.0 + 3.0 * trail_attraction * route_weight)  # Strong trail bonus
        
        # Water attraction
        water_attraction = terrain.get_water_attraction(target_row, target_col)
        weight *= (1.0 + 0.5 * water_attraction)
        
        return max(weight, 0.0)
    
    def _create_snapshot(
        self,
        probability_grid: np.ndarray,
        terrain: TerrainModel,
        timestamp: datetime,
        hours_elapsed: float
    ) -> TimeSnapshot:
        """
        Create a snapshot from the current probability grid.
        
        Only includes cells with significant probability to reduce data size.
        """
        threshold = 0.0001  # Only include cells with >0.01% probability
        
        grid_cells = []
        for row in range(probability_grid.shape[0]):
            for col in range(probability_grid.shape[1]):
                prob = probability_grid[row, col]
                
                if prob >= threshold:
                    lat, lon = terrain.grid_to_lat_lon(row, col)
                    grid_cells.append(GridCell(
                        latitude=lat,
                        longitude=lon,
                        probability=float(prob),
                        elevation=float(terrain.elevation_grid[row, col])
                    ))
        
        # Sort by probability descending
        grid_cells.sort(key=lambda c: c.probability, reverse=True)
        
        return TimeSnapshot(
            timestamp=timestamp.isoformat(),
            hours_elapsed=hours_elapsed,
            grid_cells=grid_cells,
            max_probability=float(np.max(probability_grid)) if grid_cells else 0.0,
            mean_probability=float(np.mean(probability_grid))
        )
    
    def _generate_synthetic_elevation(self, grid_size: int) -> np.ndarray:
        """Generate synthetic elevation data for testing"""
        # Create a simple terrain with some hills
        x = np.linspace(-1, 1, grid_size)
        y = np.linspace(-1, 1, grid_size)
        X, Y = np.meshgrid(x, y)
        
        # Multiple sine waves for varied terrain
        elevation = (
            100 * np.sin(3 * X) * np.cos(3 * Y) +
            50 * np.sin(5 * X + 1) +
            75 * np.cos(4 * Y + 0.5) +
            200  # Base elevation
        )
        
        return elevation
