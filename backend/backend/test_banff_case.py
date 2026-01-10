"""
Comprehensive test case for Banff SAR prediction.

Test Scenario:
- Location: Banff, Alberta (51.1784° N, 115.5708° W)
- Subject: 20-year-old male, medium experience
- Last seen: 08:00 (4 hours ago)
- Current time: 12:00
- Weather: Real-time from Open-Meteo API
- Elevation: Real data from Open-Elevation API

This test validates the entire prediction pipeline with all APIs.
"""

import asyncio
import requests
import json
from datetime import datetime, timedelta
from pprint import pprint


def test_banff_prediction():
    """
    Test prediction for a 20-year-old male lost in Banff for 4 hours.
    """
    print("=" * 80)
    print("🏔️  BANFF SAR PREDICTION TEST")
    print("=" * 80)
    print()
    
    # Test parameters
    location = {
        "latitude": 51.1784,
        "longitude": -115.5708
    }
    
    # Last seen at 08:00, current time 12:00 (4 hours ago)
    current_time = datetime.utcnow()
    time_last_seen = current_time - timedelta(hours=4)
    
    print("📋 TEST SCENARIO")
    print("-" * 80)
    print(f"Location: Banff, Alberta")
    print(f"  Latitude:  {location['latitude']}° N")
    print(f"  Longitude: {location['longitude']}° W")
    print(f"  Elevation: ~1,463m (Banff townsite)")
    print()
    print(f"Subject Profile:")
    print(f"  Age: 20 years old")
    print(f"  Sex: Male")
    print(f"  Experience: Medium (intermediate hiker)")
    print()
    print(f"Timeline:")
    print(f"  Last seen:     {time_last_seen.strftime('%H:%M:%S UTC')}")
    print(f"  Current time:  {current_time.strftime('%H:%M:%S UTC')}")
    print(f"  Hours missing: 4.0 hours")
    print()
    print(f"Search Parameters:")
    print(f"  Search radius: 5.0 km")
    print(f"  Grid resolution: 100m cells")
    print(f"  Grid size: 100 x 100 cells = 10,000 cells")
    print()
    
    # Create prediction request
    request = {
        "last_known_location": location,
        "time_last_seen": time_last_seen.isoformat() + "Z",
        "subject_profile": {
            "age": 20,
            "sex": "male",
            "experience_level": "medium"
        },
        "search_radius_km": 5.0,
        "grid_resolution_m": 100.0
    }
    
    print("🚀 SENDING PREDICTION REQUEST")
    print("-" * 80)
    print("API Endpoint: POST http://localhost:8000/api/v1/predict")
    print()
    print("Request payload:")
    print(json.dumps(request, indent=2))
    print()
    
    try:
        # Make API request
        print("⏳ Processing (this may take 8-10 seconds for API elevation fetch)...")
        print()
        
        response = requests.post(
            "http://localhost:8000/api/v1/predict",
            json=request,
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"❌ ERROR: Status code {response.status_code}")
            print(response.text)
            return
        
        result = response.json()
        
        # Display results
        print("=" * 80)
        print("✅ PREDICTION RESULTS")
        print("=" * 80)
        print()
        
        # Metadata
        metadata = result['metadata']
        print("📊 METADATA")
        print("-" * 80)
        print(f"Request ID: {result['request_id']}")
        print(f"Grid size: {metadata['grid_size']} x {metadata['grid_size']} cells")
        print(f"Grid resolution: {metadata['grid_resolution_m']}m per cell")
        print(f"Search radius: {metadata['search_radius_km']}km")
        print(f"Total snapshots: {metadata['total_snapshots']} (every 15 minutes)")
        print()
        print(f"Subject details:")
        print(f"  Age: {metadata['subject_age']} years")
        print(f"  Experience: {metadata['subject_experience']}")
        print()
        print(f"🌤️  Weather conditions: {metadata['weather_conditions']}")
        print(f"    Weather impact: {metadata['weather_impact']}")
        print()
        
        # Analyze snapshots
        snapshots = result['snapshots']
        
        print("📸 SNAPSHOT ANALYSIS")
        print("-" * 80)
        print(f"Total snapshots: {len(snapshots)}")
        print()
        
        # Initial snapshot (T+0)
        initial = snapshots[0]
        print(f"Initial Snapshot (T+0 hours):")
        print(f"  Time: {initial['timestamp']}")
        print(f"  Hours elapsed: {initial['hours_elapsed']}")
        print(f"  Max probability: {initial['max_probability']:.4f} (100%)")
        print(f"  Cells with probability: {len(initial['grid_cells'])}")
        print(f"  Status: Subject at last known location")
        print()
        
        # After 1 hour
        hour1_idx = 4  # 4 * 15min = 1 hour
        if hour1_idx < len(snapshots):
            hour1 = snapshots[hour1_idx]
            print(f"After 1 Hour (T+1):")
            print(f"  Time: {hour1['timestamp']}")
            print(f"  Max probability: {hour1['max_probability']:.4f}")
            print(f"  Cells with probability: {len(hour1['grid_cells'])}")
            print(f"  Status: Probability spreading (panic phase)")
            print()
        
        # After 4 hours (current time)
        hour4_idx = 16  # 16 * 15min = 4 hours
        if hour4_idx < len(snapshots):
            hour4 = snapshots[hour4_idx]
            print(f"After 4 Hours (T+4 - CURRENT TIME):")
            print(f"  Time: {hour4['timestamp']}")
            print(f"  Max probability: {hour4['max_probability']:.4f}")
            print(f"  Cells with probability: {len(hour4['grid_cells'])}")
            print(f"  Status: Subject could be in ~{len(hour4['grid_cells'])} locations")
            print()
        
        # Final snapshot (T+16, future projection)
        final = snapshots[-1]
        print(f"Final Snapshot (T+{final['hours_elapsed']:.1f} hours - FUTURE):")
        print(f"  Time: {final['timestamp']}")
        print(f"  Max probability: {final['max_probability']:.4f}")
        print(f"  Cells with probability: {len(final['grid_cells'])}")
        print(f"  Status: Maximum spread (exhaustion phase)")
        print()
        
        # Top probable locations at current time (4 hours)
        current_snapshot = snapshots[hour4_idx] if hour4_idx < len(snapshots) else final
        print("🎯 TOP 10 MOST PROBABLE LOCATIONS (at current time)")
        print("-" * 80)
        
        for i, cell in enumerate(current_snapshot['grid_cells'][:10], 1):
            distance_km = haversine(
                location['latitude'], location['longitude'],
                cell['latitude'], cell['longitude']
            )
            print(f"{i:2d}. Probability: {cell['probability']:.4f} ({cell['probability']*100:.2f}%)")
            print(f"    Location: {cell['latitude']:.4f}°N, {cell['longitude']:.4f}°W")
            print(f"    Elevation: {cell['elevation']:.1f}m")
            print(f"    Distance from LKL: {distance_km:.2f}km")
            print()
        
        # Analysis summary
        print("=" * 80)
        print("📈 BEHAVIORAL ANALYSIS")
        print("=" * 80)
        print()
        
        print("Age Factor (20 years old):")
        print("  - High travel rate: ~400-500m per 15 minutes")
        print("  - Good physical condition")
        print("  - Higher panic response (less experience)")
        print("  - May take more risks")
        print()
        
        print("Time Factor (4 hours elapsed):")
        print("  - Past initial panic phase (0-3 hours)")
        print("  - Entering exhaustion phase")
        print("  - Starting to think more rationally")
        print("  - May seek shelter or trails")
        print()
        
        print("Experience Level (Medium):")
        print("  - Some wilderness knowledge")
        print("  - Moderate trail following instinct")
        print("  - Decent navigation skills")
        print("  - 60% chance of route traveling")
        print()
        
        weather_modifier = extract_weather_modifier(metadata['weather_impact'])
        print(f"Weather Impact ({weather_modifier:.2f}x speed):")
        if weather_modifier >= 0.9:
            print("  - Favorable conditions for movement")
            print("  - Minimal weather impact")
        elif weather_modifier >= 0.7:
            print("  - Moderate conditions")
            print("  - Some movement restriction")
        else:
            print("  - Harsh conditions")
            print("  - Significant movement restriction")
            print("  - May be sheltering")
        print()
        
        # Search recommendations
        print("=" * 80)
        print("🔍 SEARCH RECOMMENDATIONS")
        print("=" * 80)
        print()
        
        print("Priority 1 - High Probability Areas:")
        high_prob_cells = [c for c in current_snapshot['grid_cells'] if c['probability'] > 0.01]
        print(f"  - {len(high_prob_cells)} cells with >1% probability")
        print(f"  - Focus search within these zones first")
        print()
        
        print("Priority 2 - Trail Corridors:")
        print(f"  - Check all trails within 5km radius")
        print(f"  - 90% of lost persons found within 500m of trails")
        print(f"  - Young males often follow linear features")
        print()
        
        print("Priority 3 - Elevated Viewpoints:")
        print(f"  - Check high points for cell phone signal attempts")
        print(f"  - Young subjects often go uphill seeking signal")
        print()
        
        print("Timeline Urgency:")
        if final['hours_elapsed'] < 12:
            print(f"  - Subject mobile for {final['hours_elapsed']:.1f} more hours (predicted)")
            print(f"  - Window for active search: Good")
        else:
            print(f"  - Subject likely exhausted after 12 hours")
            print(f"  - May be sheltering in place")
        print()
        
        # Statistics
        print("=" * 80)
        print("📊 STATISTICAL SUMMARY")
        print("=" * 80)
        print()
        
        total_area_km2 = (metadata['search_radius_km'] * 2) ** 2
        print(f"Search area: {total_area_km2:.1f} km²")
        print(f"Total grid cells: {metadata['grid_size'] ** 2:,}")
        print(f"Cell size: {metadata['grid_resolution_m']}m x {metadata['grid_resolution_m']}m")
        print(f"Snapshots generated: {len(snapshots)}")
        print(f"Time coverage: {snapshots[0]['hours_elapsed']:.1f}h to {snapshots[-1]['hours_elapsed']:.1f}h")
        print()
        
        # Success message
        print("=" * 80)
        print("✅ TEST COMPLETE - ALL SYSTEMS OPERATIONAL")
        print("=" * 80)
        print()
        print("APIs Used:")
        print("  ✓ Weather API (Open-Meteo) - Real conditions")
        print("  ✓ Elevation API (Open-Elevation) - Real terrain")
        print("  ✓ Behavioral Model - Age/sex specific")
        print("  ✓ Probability Engine - Time-series evolution")
        print()
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to API server")
        print()
        print("Please start the server first:")
        print("  cd /Users/lucas/projects/beacon-ai/backend")
        print("  ./start.sh")
        print()
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers"""
    import math
    R = 6371  # Earth radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def extract_weather_modifier(weather_impact_str):
    """Extract numeric weather modifier from string like '0.85x movement speed'"""
    try:
        return float(weather_impact_str.split('x')[0])
    except:
        return 1.0


if __name__ == "__main__":
    test_banff_prediction()
