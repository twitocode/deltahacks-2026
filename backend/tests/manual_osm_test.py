
import asyncio
import sys
import os
import json

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.osm_loader import OSMLoader

async def main():
    print("Testing OSMLoader (Overpass API)...")
    loader = OSMLoader()
    
    # Banff coordinates (approximate bounding box)
    # Center: 51.1784° N, 115.5708° W
    # ~2km box
    lat = 51.1784
    lon = -115.5708
    delta = 0.02 # approx 2km
    
    min_lat, max_lat = lat - delta, lat + delta
    min_lon, max_lon = lon - delta, lon + delta
    
    print(f"Fetching OSM data for bounding box:")
    print(f"  Lat: {min_lat:.4f} to {max_lat:.4f}")
    print(f"  Lon: {min_lon:.4f} to {max_lon:.4f}")
    
    data = await loader.fetch_osm_data(min_lat, min_lon, max_lat, max_lon)
    
    if data:
        print("\n✅ OSM data received.")
        print(f"Generator: {data.get('generator', 'Unknown')}")
        
        elements = data.get('elements', [])
        print(f"Total elements found: {len(elements)}")
        
        # Manually trigger parsing to test data processing
        print("Parsing elements...")
        points = 0
        ways = 0
        
        for element in elements:
            if element['type'] == 'node':
                points += 1
            elif element['type'] == 'way':
                ways += 1
                loader._parse_way(element)
                
        print(f"  Nodes: {points}")
        print(f"  Ways: {ways}")
        
        print("\nProcessed Features:")
        print(f"  Trails loaded: {len(loader.trails)}")
        print(f"  Roads loaded: {len(loader.roads)}")
        print(f"  Water features loaded: {len(loader.water_features)}")
        
        if loader.trails:
            print(f"  Example Trail: {loader.trails[0]['name']} ({loader.trails[0]['type']})")
            
        # Test distance calculation
        dist = loader.get_nearest_trail_distance(lat, lon)
        print(f"\nDistance to nearest trail from center: {dist:.1f} meters")

    else:
        print("\n❌ Failed to fetch OSM data.")

if __name__ == "__main__":
    asyncio.run(main())
