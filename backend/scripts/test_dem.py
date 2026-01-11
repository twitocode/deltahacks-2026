#!/usr/bin/env python3
"""
DEM Tile Testing Script

Developer tool to download and test DEM tiles for any location.
Useful for pre-populating the cache before demo.

Usage:
    # Download tile for Banff
    python test_dem.py --lat 51.178 --lon -115.570
    
    # Download tile and show info
    python test_dem.py --lat 51.178 --lon -115.570 --info
    
    # List cached tiles
    python test_dem.py --list
    
    # Clear cache
    python test_dem.py --clear
    
    # Test elevation lookup
    python test_dem.py --lat 51.178 --lon -115.570 --elevation
"""

import argparse
import sys
import math
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.dem.dem_loader import get_dem_loader, reset_dem_loader, MeritDEMLoader


def download_tile(lat: float, lon: float, show_info: bool = False):
    """Download and optionally display info for a tile."""
    loader = get_dem_loader(cleanup_on_exit=False)  # Keep tiles
    
    tile_lat = math.floor(lat)
    tile_lon = math.floor(lon)
    
    print(f"\n{'='*50}")
    print(f"DEM Tile Download")
    print(f"{'='*50}")
    print(f"Location: ({lat}, {lon})")
    print(f"Tile: merit_{tile_lat}_{tile_lon}.tif")
    print(f"Tile bounds: {loader.get_tile_bounds(tile_lat, tile_lon)}")
    print()
    
    try:
        print("Downloading/loading tile...")
        tile = loader.load_tile(tile_lat, tile_lon)
        print(f"✓ Tile loaded successfully!")
        
        if show_info:
            print(f"\nTile Info:")
            print(f"  Shape: {tile.data.shape}")
            print(f"  CRS: {tile.crs}")
            print(f"  Bounds: {tile.bounds}")
            print(f"  Min elevation: {tile.data[tile.data > -500].min():.1f}m")
            print(f"  Max elevation: {tile.data.max():.1f}m")
            print(f"  Mean elevation: {tile.data[tile.data > -500].mean():.1f}m")
        
        print(f"\nCache stats:")
        stats = loader.get_cache_stats()
        print(f"  Memory cache: {stats['memory_cache_size']}/{stats['memory_cache_max']}")
        print(f"  Disk tiles: {stats['disk_tiles']}")
        print(f"  Memory tiles: {stats['memory_tiles']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def get_elevation(lat: float, lon: float):
    """Get elevation at a point."""
    loader = get_dem_loader(cleanup_on_exit=False)
    
    print(f"\n{'='*50}")
    print(f"Elevation Lookup")
    print(f"{'='*50}")
    print(f"Location: ({lat}, {lon})")
    
    try:
        elevation = loader.get_elevation_at_point(lat, lon)
        if elevation is not None:
            print(f"✓ Elevation: {elevation:.1f}m")
        else:
            print(f"✗ No elevation data available")
        return elevation
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def test_search_area(lat: float, lon: float, radius_km: float):
    """Test loading a search area."""
    loader = get_dem_loader(cleanup_on_exit=False)
    
    print(f"\n{'='*50}")
    print(f"Search Area Test")
    print(f"{'='*50}")
    print(f"Center: ({lat}, {lon})")
    print(f"Radius: {radius_km}km")
    
    try:
        # Validate single tile
        tile_lat, tile_lon = loader.validate_single_tile(lat, lon, radius_km)
        print(f"✓ Fits in single tile: merit_{tile_lat}_{tile_lon}.tif")
        
        # Load data
        dem_data = loader.get_elevation_for_search(lat, lon, radius_km)
        print(f"✓ Loaded elevation grid: {dem_data.elevation.shape}")
        print(f"  Bounds: {dem_data.metadata.bounds}")
        print(f"  Min: {dem_data.elevation[dem_data.elevation > -500].min():.1f}m")
        print(f"  Max: {dem_data.elevation.max():.1f}m")
        
        return True
        
    except ValueError as e:
        print(f"✗ Single-tile constraint violated: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def list_tiles():
    """List all cached tiles."""
    loader = get_dem_loader(cleanup_on_exit=False)
    
    print(f"\n{'='*50}")
    print(f"Cached Tiles")
    print(f"{'='*50}")
    
    disk_tiles = loader.list_cached_tiles()
    memory_tiles = loader.list_memory_cache()
    
    print(f"On disk ({len(disk_tiles)}):")
    for t in sorted(disk_tiles):
        mem_marker = " [in memory]" if t in memory_tiles else ""
        print(f"  - {t}{mem_marker}")
    
    if not disk_tiles:
        print("  (none)")
    
    print(f"\nIn memory ({len(memory_tiles)}):")
    for t in memory_tiles:
        print(f"  - {t}")
    
    if not memory_tiles:
        print("  (none)")


def clear_cache():
    """Clear all cached tiles."""
    loader = get_dem_loader(cleanup_on_exit=False)
    
    print(f"\n{'='*50}")
    print(f"Clearing Cache")
    print(f"{'='*50}")
    
    stats = loader.get_cache_stats()
    print(f"Before: {stats['disk_tiles']} disk, {stats['memory_cache_size']} memory")
    
    loader.clear_cache()
    
    stats = loader.get_cache_stats()
    print(f"After: {stats['disk_tiles']} disk, {stats['memory_cache_size']} memory")
    print("✓ Cache cleared")


def main():
    parser = argparse.ArgumentParser(
        description="DEM Tile Testing Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download tile for Banff, show info
  python test_dem.py --lat 51.178 --lon -115.570 --info
  
  # Get elevation at a point
  python test_dem.py --lat 51.178 --lon -115.570 --elevation
  
  # Test 5km search area
  python test_dem.py --lat 51.178 --lon -115.570 --radius 5
  
  # List cached tiles
  python test_dem.py --list
  
  # Clear cache
  python test_dem.py --clear
"""
    )
    
    parser.add_argument("--lat", type=float, help="Latitude")
    parser.add_argument("--lon", type=float, help="Longitude")
    parser.add_argument("--radius", type=float, help="Search radius in km (for testing)")
    parser.add_argument("--info", action="store_true", help="Show tile info")
    parser.add_argument("--elevation", action="store_true", help="Get elevation at point")
    parser.add_argument("--list", action="store_true", help="List cached tiles")
    parser.add_argument("--clear", action="store_true", help="Clear cache")
    
    args = parser.parse_args()
    
    if args.list:
        list_tiles()
        return
    
    if args.clear:
        clear_cache()
        return
    
    if args.lat is None or args.lon is None:
        parser.print_help()
        return
    
    if args.elevation:
        get_elevation(args.lat, args.lon)
    elif args.radius:
        test_search_area(args.lat, args.lon, args.radius)
    else:
        download_tile(args.lat, args.lon, args.info)


if __name__ == "__main__":
    main()
