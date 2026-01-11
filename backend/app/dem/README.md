# DEM Loader Module

Single-tile DEM loading with in-memory caching.

## Features

- **Single-Tile Constraint**: All searches must fit within one 1x1° tile
- **LRU Memory Cache**: O(1) lookups for cached tiles (max 4 tiles)
- **Auto-Download**: Fetches from NASA SRTM COG on first request
- **Session Cleanup**: Optional auto-delete of tiles on server shutdown

## Quick Start

```python
from app.dem.dem_loader import get_dem_loader

loader = get_dem_loader(cleanup_on_exit=False)  # Keep tiles for dev

# Get elevation at a point (O(1) after first load)
elevation = loader.get_elevation_at_point(51.178, -115.570)

# Load search area (validates single-tile constraint)
dem_data = loader.get_elevation_for_search(
    center_lat=51.178,
    center_lon=-115.570,
    radius_km=5.0
)
```

## Developer Testing

```bash
cd backend

# Download tile for Banff
python scripts/test_dem.py --lat 51.178 --lon -115.570 --info

# Test 5km search area
python scripts/test_dem.py --lat 51.178 --lon -115.570 --radius 5

# Get elevation
python scripts/test_dem.py --lat 51.178 --lon -115.570 --elevation

# List cached tiles
python scripts/test_dem.py --list

# Clear cache
python scripts/test_dem.py --clear
```

## Single-Tile Constraint

Each tile covers 1°×1° (~70km × 111km at 50°N). Max safe radius = ~35km.

If search spans multiple tiles, you'll get an error with max safe radius:
```
ValueError: Search radius 40km spans multiple tiles. Max radius for this location: 32.5km
```

## Cache Stats

```python
loader.get_cache_stats()
# {'memory_cache_size': 2, 'memory_cache_max': 4, 'disk_tiles': 6, ...}
```

## Data Source

[NASA SRTM v3 1-arcsecond](https://data.naturalcapitalalliance.stanford.edu/) (~30m resolution)
