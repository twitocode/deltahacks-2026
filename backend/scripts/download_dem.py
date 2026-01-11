#!/usr/bin/env python3
"""
MERIT DEM Downloader

Downloads MERIT DEM GeoTIFF tiles for a specified geographic region.
Tiles are named merit_{lat}_{lon}.tif where lat/lon are integer floor values.

MERIT DEM source: http://hydro.iis.u-tokyo.ac.jp/~yamadai/MERIT_DEM/
Alternative: OpenTopography API

Usage:
    python download_dem.py --lat 51.178 --lon -115.570 --radius 50
    python download_dem.py --bounds 50,-117,52,-114
    python download_dem.py --tiles 51,-116 51,-115 50,-116
"""

import argparse
import math
import os
import sys
from pathlib import Path
from typing import List, Tuple
import urllib.request
import urllib.error

# Default output directory (relative to this script)
DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "elevation" / "merit"

# MERIT DEM tile sources
# Note: MERIT DEM requires registration. These are example URLs.
# You may need to use OpenTopography or another source.

# OpenTopography API (requires API key)
OPENTOPOGRAPHY_BASE = "https://portal.opentopography.org/API/globaldem"

# Alternative: AWS Open Data (Copernicus DEM)
COPERNICUS_BASE = "https://copernicus-dem-30m.s3.amazonaws.com"


def get_tiles_for_bounds(
    west: float, south: float, east: float, north: float
) -> List[Tuple[int, int]]:
    """
    Get list of tile coordinates needed to cover the bounding box.
    
    Returns:
        List of (lat, lon) integer tuples for tile names
    """
    lat_min = math.floor(south)
    lat_max = math.floor(north)
    lon_min = math.floor(west)
    lon_max = math.floor(east)
    
    tiles = []
    for lat in range(lat_min, lat_max + 1):
        for lon in range(lon_min, lon_max + 1):
            tiles.append((lat, lon))
    
    return tiles


def get_tiles_for_center(
    center_lat: float, center_lon: float, radius_km: float
) -> List[Tuple[int, int]]:
    """
    Get tiles needed to cover a circular area around a center point.
    """
    # Convert radius to degrees (approximate)
    delta_lat = radius_km / 111.32
    delta_lon = radius_km / (111.32 * abs(math.cos(math.radians(center_lat))))
    
    west = center_lon - delta_lon
    east = center_lon + delta_lon
    south = center_lat - delta_lat
    north = center_lat + delta_lat
    
    return get_tiles_for_bounds(west, south, east, north)


def tile_filename(lat: int, lon: int) -> str:
    """Generate filename for a tile."""
    return f"merit_{lat}_{lon}.tif"


def download_from_opentopography(
    lat: int, lon: int, output_dir: Path, api_key: str
) -> bool:
    """
    Download DEM tile from OpenTopography API.
    
    Requires free API key from: https://opentopography.org/
    """
    # Tile bounds (1x1 degree)
    south, north = lat, lat + 1
    west, east = lon, lon + 1
    
    url = (
        f"{OPENTOPOGRAPHY_BASE}?"
        f"demtype=SRTMGL1"  # or COP30 for Copernicus
        f"&south={south}&north={north}&west={west}&east={east}"
        f"&outputFormat=GTiff"
        f"&API_Key={api_key}"
    )
    
    output_path = output_dir / tile_filename(lat, lon)
    
    try:
        print(f"  Downloading from OpenTopography: ({lat}, {lon})...")
        urllib.request.urlretrieve(url, output_path)
        print(f"  ✓ Saved to {output_path}")
        return True
    except urllib.error.HTTPError as e:
        print(f"  ✗ HTTP Error {e.code}: {e.reason}")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def download_from_copernicus(lat: int, lon: int, output_dir: Path) -> bool:
    """
    Download DEM tile from Copernicus DEM (AWS Open Data).
    
    Free, no API key required.
    """
    # Copernicus uses specific naming: Copernicus_DSM_COG_10_N51_00_W116_00_DEM
    lat_prefix = "N" if lat >= 0 else "S"
    lon_prefix = "E" if lon >= 0 else "W"
    
    lat_str = f"{abs(lat):02d}"
    lon_str = f"{abs(lon):03d}"
    
    tile_name = f"Copernicus_DSM_COG_10_{lat_prefix}{lat_str}_00_{lon_prefix}{lon_str}_00_DEM"
    url = f"{COPERNICUS_BASE}/{tile_name}/{tile_name}.tif"
    
    output_path = output_dir / tile_filename(lat, lon)
    
    try:
        print(f"  Downloading Copernicus DEM: ({lat}, {lon})...")
        urllib.request.urlretrieve(url, output_path)
        print(f"  ✓ Saved to {output_path}")
        return True
    except urllib.error.HTTPError as e:
        print(f"  ✗ HTTP Error {e.code}: {e.reason}")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def download_tile(
    lat: int, lon: int, 
    output_dir: Path, 
    source: str = "copernicus",
    api_key: str = None
) -> bool:
    """Download a single DEM tile."""
    output_path = output_dir / tile_filename(lat, lon)
    
    # Check if already exists
    if output_path.exists():
        print(f"  ⊘ Already exists: {output_path.name}")
        return True
    
    if source == "opentopography":
        if not api_key:
            print("  ✗ OpenTopography requires API key (--api-key)")
            return False
        return download_from_opentopography(lat, lon, output_dir, api_key)
    elif source == "copernicus":
        return download_from_copernicus(lat, lon, output_dir)
    else:
        print(f"  ✗ Unknown source: {source}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Download MERIT/Copernicus DEM tiles for a region",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download tiles for 50km radius around Banff
  python download_dem.py --lat 51.178 --lon -115.570 --radius 50
  
  # Download tiles for bounding box
  python download_dem.py --bounds 50,-117,52,-114
  
  # Download specific tiles
  python download_dem.py --tiles 51,-116 51,-115 50,-116
  
  # Use OpenTopography (requires API key)
  python download_dem.py --lat 51.178 --lon -115.570 --radius 50 \\
      --source opentopography --api-key YOUR_KEY
"""
    )
    
    # Location options (mutually exclusive groups)
    loc_group = parser.add_mutually_exclusive_group(required=True)
    loc_group.add_argument(
        "--tiles", nargs="+", metavar="LAT,LON",
        help="Specific tiles to download (e.g., 51,-116 50,-115)"
    )
    loc_group.add_argument(
        "--bounds", metavar="S,W,N,E",
        help="Bounding box: south,west,north,east"
    )
    
    # For center+radius mode
    parser.add_argument("--lat", type=float, help="Center latitude")
    parser.add_argument("--lon", type=float, help="Center longitude")
    parser.add_argument("--radius", type=float, default=25, 
                       help="Radius in km (default: 25)")
    
    # Output options
    parser.add_argument(
        "--output", "-o", type=Path, default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})"
    )
    parser.add_argument(
        "--source", choices=["copernicus", "opentopography"],
        default="copernicus",
        help="DEM source (default: copernicus)"
    )
    parser.add_argument(
        "--api-key", 
        help="API key for OpenTopography"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show tiles without downloading"
    )
    
    args = parser.parse_args()
    
    # Handle center+radius mode (if lat/lon provided without --tiles or --bounds)
    if args.lat is not None and args.lon is not None:
        tiles = get_tiles_for_center(args.lat, args.lon, args.radius)
    elif args.tiles:
        tiles = []
        for t in args.tiles:
            parts = t.replace(",", " ").split()
            if len(parts) == 2:
                tiles.append((int(parts[0]), int(parts[1])))
            else:
                print(f"Invalid tile format: {t}")
                sys.exit(1)
    elif args.bounds:
        parts = [float(x) for x in args.bounds.split(",")]
        if len(parts) != 4:
            print("Bounds must be: south,west,north,east")
            sys.exit(1)
        south, west, north, east = parts
        tiles = get_tiles_for_bounds(west, south, east, north)
    else:
        parser.print_help()
        sys.exit(1)
    
    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*50}")
    print(f"DEM Downloader")
    print(f"{'='*50}")
    print(f"Source: {args.source}")
    print(f"Output: {args.output}")
    print(f"Tiles:  {len(tiles)}")
    print(f"{'='*50}\n")
    
    # Show tiles
    for lat, lon in sorted(tiles):
        print(f"  [{lat:3d}, {lon:4d}] -> {tile_filename(lat, lon)}")
    
    if args.dry_run:
        print("\n(Dry run - no files downloaded)")
        return
    
    print(f"\nDownloading {len(tiles)} tiles...\n")
    
    success = 0
    failed = 0
    
    for lat, lon in tiles:
        if download_tile(lat, lon, args.output, args.source, args.api_key):
            success += 1
        else:
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Complete: {success} downloaded, {failed} failed")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
