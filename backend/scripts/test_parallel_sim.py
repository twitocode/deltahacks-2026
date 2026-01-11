
import asyncio
import logging
import sys
import os
from datetime import datetime

# Add app to path
sys.path.append(os.getcwd())

from app.config import get_settings
from app.simulation.simulator import get_simulator
from app.simulation.models import HikerProfile, Gender

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting Parallel Simulation Verification")
    
    # 1. Override Settings
    settings = get_settings()
    settings.parallel_agents = True
    settings.max_workers = 2
    settings.num_agents = 50 # Enough to trigger chunks
    settings.timestep_minutes = 15
    
    logger.info(f"Settings: parallel={settings.parallel_agents}, workers={settings.max_workers}, agents={settings.num_agents}")
    
    # 2. Setup Simulation Params
    center_lat = 49.0
    center_lon = -120.0
    radius_km = 5.0
    
    profile = HikerProfile(
        age=30,
        gender=Gender.MALE,
        skill_level=3
    )
    
    current_time = datetime.now()
    
    # 3. Run Simulation
    sim = get_simulator()
    
    start_time = datetime.now()
    try:
        result = await sim.run_simulation(
            center_lat=center_lat,
            center_lon=center_lon,
            radius_km=radius_km,
            profile=profile,
            current_time=current_time
        )
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"Simulation completed in {duration:.2f} seconds")
        logger.info(f"Time slices generated: {len(result.time_slices)}")
        logger.info(f"Final positions count: {len(result.final_positions)}")
        
        if len(result.time_slices) > 0 and len(result.final_positions) > 0:
            logger.info("✅ Verification SUCCESS: Simulation produced results")
        else:
            logger.error("❌ Verification FAILED: No results produced")
            
    except Exception as e:
        logger.error(f"❌ Verification FAILED with error: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
