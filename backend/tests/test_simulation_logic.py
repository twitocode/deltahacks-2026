
import math
import unittest
from datetime import datetime
from app.simulation.models import HikerProfile, Gender, WeatherConditions
from app.simulation.simulator import Agent, Strategy

class TestSimulationLogic(unittest.TestCase):
    
    def test_gender_speeds(self):
        """Verify male and female base speeds."""
        male = HikerProfile(gender=Gender.MALE, age=30, skill_level=1) # normalize skill
        female = HikerProfile(gender=Gender.FEMALE, age=30, skill_level=1)
        
        # Skill level 1 adds 0.7 multiplier (0.6 + 0.1)
        # Age 30 has small decay: (30-25)/10 * 0.012 = 0.5 * 0.012 = 0.006
        # Male base: 1.317 - 0.006 = 1.311
        # Female base: 1.241 - 0.006 = 1.235
        
        # Taking raw base speeds roughly (ignoring exact floating point of decay for a sec)
        # Actually lets check relative difference
        # Female speed should be approx 94.3% of Male
        
        ratio = female.speed_factor / male.speed_factor
        self.assertAlmostEqual(ratio, 0.942, places=2)
        print(f"Gender Speed Ratio: {ratio:.3f} (Target ~0.943)")

    def test_tobler_function(self):
        """Verify Tobler's hiking function output."""
        # W = 6 * exp(-3.5 * |dh/dx + 0.05|) km/h
        
        def tobler_mps(slope):
            kmh = 6 * math.exp(-3.5 * abs(slope + 0.05))
            return kmh / 3.6

        # Flat ground (slope 0)
        flat_speed = tobler_mps(0.0)
        # Exp(-3.5 * 0.05) = exp(-0.175) = 0.839
        # 6 * 0.839 = 5.03 km/h = 1.39 m/s
        print(f"Tobler Flat Speed: {flat_speed:.3f} m/s")
        self.assertTrue(1.3 < flat_speed < 1.5)

        # Uphill 10% (0.1)
        # Exp(-3.5 * 0.15) = exp(-0.525) = 0.59
        # 6 * 0.59 = 3.55 km/h
        # Drop from 5.03 to 3.55 is approx 30% reduction.
        uphill_speed = tobler_mps(0.1)
        print(f"Tobler Uphill 10% Speed: {uphill_speed:.3f} m/s")
        
        reduction = 1.0 - (uphill_speed / flat_speed)
        print(f"Tobler Reduction at 10% Grade: {reduction*100:.1f}%")
        self.assertTrue(0.25 < reduction < 0.35)

    def test_weather_penalty(self):
        """Verify rain penalty is exactly 8%."""
        w = WeatherConditions(precipitation_mm=5.0) # > 0
        self.assertEqual(w.movement_penalty, 0.08)
        print(f"Rain Penalty: {w.movement_penalty}")

if __name__ == '__main__':
    unittest.main()
