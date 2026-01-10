import numpy as np
from enum import Enum
from app.models.schemas import ExperienceLevel, Sex


class MovementStrategy(Enum):
    """Common lost person movement strategies"""
    ROUTE_TRAVELING = "route_traveling"  # Following trails/paths
    BACKTRACKING = "backtracking"  # Attempting to return
    RANDOM_TRAVELING = "random_traveling"  # No clear goal
    DIRECTION_TRAVELING = "direction_traveling"  # Picking a direction
    STAYING_PUT = "staying_put"  # Not moving
    UPHILL_SEEKING = "uphill_seeking"  # Looking for cell signal/view
    DOWNHILL_SEEKING = "downhill_seeking"  # Traditional lost behavior


class BehaviorModel:
    """Models human behavior patterns for lost hikers"""
    
    # Base travel distances per 15 minutes (in meters) by age/sex
    BASE_TRAVEL_RATES = {
        # (age_group, sex): meters per 15 min
        ("young_male", Sex.MALE): 400,  # 20-40 years, fit
        ("young_female", Sex.FEMALE): 350,
        ("adult_male", Sex.MALE): 300,  # 40-60 years
        ("adult_female", Sex.FEMALE): 275,
        ("senior_male", Sex.MALE): 200,  # 60+ years
        ("senior_female", Sex.FEMALE): 175,
        ("child", Sex.UNKNOWN): 250,  # Under 18
    }
    
    @staticmethod
    def get_age_group(age: int, sex: Sex) -> str:
        """Categorize age into groups for behavior modeling"""
        if age < 18:
            return "child"
        elif age < 40:
            return f"young_{sex.value}" if sex != Sex.UNKNOWN else "young_male"
        elif age < 60:
            return f"adult_{sex.value}" if sex != Sex.UNKNOWN else "adult_male"
        else:
            return f"senior_{sex.value}" if sex != Sex.UNKNOWN else "senior_male"
    
    @staticmethod
    def get_base_travel_rate(age: int, sex: Sex) -> float:
        """Get base travel rate in meters per 15 minutes"""
        age_group = BehaviorModel.get_age_group(age, sex)
        
        # Try exact match first
        if (age_group, sex) in BehaviorModel.BASE_TRAVEL_RATES:
            return BehaviorModel.BASE_TRAVEL_RATES[(age_group, sex)]
        
        # Fallback to male rates if unknown
        key = (age_group, Sex.MALE)
        return BehaviorModel.BASE_TRAVEL_RATES.get(key, 300)
    
    @staticmethod
    def get_movement_strategy_weights(
        age: int,
        sex: Sex,
        experience: ExperienceLevel,
        hours_elapsed: float
    ) -> dict:
        """
        Get probability weights for different movement strategies.
        Weights change over time as panic, exhaustion, and survival instincts evolve.
        
        Returns:
            Dict mapping MovementStrategy to probability weight
        """
        weights = {}
        
        # Early phase (0-3 hours): Initial panic and attempt to navigate
        if hours_elapsed < 3:
            if experience == ExperienceLevel.HIGH:
                weights = {
                    MovementStrategy.BACKTRACKING: 0.35,
                    MovementStrategy.ROUTE_TRAVELING: 0.30,
                    MovementStrategy.STAYING_PUT: 0.15,
                    MovementStrategy.DIRECTION_TRAVELING: 0.10,
                    MovementStrategy.UPHILL_SEEKING: 0.10,
                }
            elif experience == ExperienceLevel.LOW or age < 18:
                weights = {
                    MovementStrategy.RANDOM_TRAVELING: 0.30,
                    MovementStrategy.DOWNHILL_SEEKING: 0.25,
                    MovementStrategy.ROUTE_TRAVELING: 0.20,
                    MovementStrategy.DIRECTION_TRAVELING: 0.15,
                    MovementStrategy.STAYING_PUT: 0.10,
                }
            else:  # MEDIUM or UNKNOWN
                weights = {
                    MovementStrategy.ROUTE_TRAVELING: 0.30,
                    MovementStrategy.BACKTRACKING: 0.20,
                    MovementStrategy.UPHILL_SEEKING: 0.20,
                    MovementStrategy.DOWNHILL_SEEKING: 0.15,
                    MovementStrategy.RANDOM_TRAVELING: 0.15,
                }
        
        # Middle phase (3-12 hours): Exhaustion setting in
        elif hours_elapsed < 12:
            if experience == ExperienceLevel.HIGH:
                weights = {
                    MovementStrategy.STAYING_PUT: 0.40,
                    MovementStrategy.ROUTE_TRAVELING: 0.25,
                    MovementStrategy.UPHILL_SEEKING: 0.20,
                    MovementStrategy.BACKTRACKING: 0.15,
                }
            else:
                weights = {
                    MovementStrategy.DOWNHILL_SEEKING: 0.30,
                    MovementStrategy.ROUTE_TRAVELING: 0.25,
                    MovementStrategy.STAYING_PUT: 0.20,
                    MovementStrategy.RANDOM_TRAVELING: 0.15,
                    MovementStrategy.DIRECTION_TRAVELING: 0.10,
                }
        
        # Late phase (12+ hours): Severe exhaustion, seeking shelter
        else:
            weights = {
                MovementStrategy.STAYING_PUT: 0.50,
                MovementStrategy.DOWNHILL_SEEKING: 0.20,
                MovementStrategy.ROUTE_TRAVELING: 0.15,
                MovementStrategy.RANDOM_TRAVELING: 0.10,
                MovementStrategy.DIRECTION_TRAVELING: 0.05,
            }
        
        return weights
    
    @staticmethod
    def apply_terrain_modifier(
        base_rate: float,
        slope_degrees: float,
        vegetation_density: float = 0.5
    ) -> float:
        """
        Modify travel rate based on terrain difficulty using Tobler's Hiking Function.
        
        Args:
            base_rate: Base travel rate in m/15min
            slope_degrees: Slope angle in degrees (positive = uphill, negative = downhill)
            vegetation_density: 0.0 (clear) to 1.0 (impassable)
        
        Returns:
            Modified travel rate
        """
        # Tobler's hiking function (simplified for 15-min intervals)
        # Speed is optimal around -5 degrees (slight downhill)
        slope_factor = np.exp(-3.5 * abs(np.deg2rad(slope_degrees) + 0.05))
        
        # Vegetation penalty
        vegetation_factor = 1.0 - (0.7 * vegetation_density)
        
        return base_rate * slope_factor * vegetation_factor
    
    @staticmethod
    def get_panic_multiplier(hours_elapsed: float) -> float:
        """
        Get movement speed multiplier based on panic level over time.
        Early hours: high panic = faster, erratic movement
        Later hours: exhaustion takes over
        """
        if hours_elapsed < 1:
            return 1.3  # Initial panic increases speed
        elif hours_elapsed < 3:
            return 1.1
        elif hours_elapsed < 8:
            return 0.9
        elif hours_elapsed < 24:
            return 0.7  # Exhaustion
        else:
            return 0.5  # Severe exhaustion
