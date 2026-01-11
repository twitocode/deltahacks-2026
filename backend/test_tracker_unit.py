
import sys
import math
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

# Mock dependencies to avoid importing the whole app
class Strategy(str, Enum):
    DIRECTION_TRAVELING = "DT"
    ROUTE_TRAVELING = "RT"
    RANDOM_WALKING = "RW"
    VIEW_ENHANCING = "VE"
    STAYING_PUT = "SP"

@dataclass
class Agent:
    id: int
    lat: float
    lon: float
    elevation: float
    strategy: Strategy
    heading: float
    steps_taken: int = 0
    energy: float = 1.0
    is_active: bool = True

# Copying AgentTracker class for testing isolation (or I could fix imports)
# But testing the class logic is better done by importing if possible.
# Let's try to mock the logger and test the logic from the actual file 
# bypassing tqdm import if possible, or just install tqdm again.

print("Installing tqdm for test...")
import subprocess
subprocess.check_call([sys.executable, "-m", "pip", "install", "tqdm"])

from app.simulation.simulator import AgentTracker, Agent as RealAgent, Strategy as RealStrategy

def test_tracker():
    print("Testing AgentTracker...")
    
    # Create agents
    agents = [
        RealAgent(id=0, lat=50.0, lon=-115.0, elevation=1000, strategy=RealStrategy.RANDOM_WALKING, heading=0),
        RealAgent(id=1, lat=50.0, lon=-115.0, elevation=1000, strategy=RealStrategy.STAYING_PUT, heading=0),
    ]
    
    # Init tracker
    tracker = AgentTracker(agents, enabled=True)
    assert tracker.tracked_id is not None
    print(f"Tracking agent {tracker.tracked_id}")
    
    # Log some events
    tracker.log_step_start(0)
    tracker.log_decision(tracker.tracked_id, "TEST", "Testing decision log")
    tracker.log_movement(tracker.tracked_id, 50.0, -115.0, 50.1, -115.0, 11100, "N", 1.0)
    tracker.log_energy(tracker.tracked_id, 1.0, 0.9, "Walking")
    
    # Test auto-switch
    tracked_agent = tracker._get_tracked_agent()
    tracked_agent.is_active = False
    
    tracker.log_step_start(1)
    new_tracked = tracker._get_tracked_agent()
    assert new_tracked.id != tracked_agent.id
    print(f"Switched to agent {new_tracked.id}")
    
    print("AgentTracker logic verified!")

if __name__ == "__main__":
    test_tracker()
