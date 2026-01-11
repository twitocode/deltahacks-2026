# DEM Loader Module

Automatic DEM (Digital Elevation Model) tile loading with caching support.

## Overview

The `MeritDEMLoader` automatically downloads elevation data from NASA SRTM when needed and caches tiles locally for fast subsequent lookups.

## Features

- **Auto-Download**: Fetches missing 1x1 degree tiles from NASA SRTM COG on first request
- **Local Caching**: Saves tiles to `data/elevation/merit/` for instant future access
- **Memory Safe**: Max 9 tiles (3x3 grid) per request, ~5km radius limit
- **HTTP Range Requests**: Only downloads needed portions from remote COG

## Quick Start

```python
from app.dem.dem_loader import get_dem_loader

# Get singleton loader instance
loader = get_dem_loader()

# Get elevation at a point (auto-downloads if needed)
elevation = loader.get_elevation_at_point(51.178, -115.570)
print(f"Elevation: {elevation}m")

# Get elevation grid for an area
bounds = (-115.6, 51.1, -115.5, 51.2)  # (west, south, east, north)
dem_data = loader.get_elevation_window(bounds)
print(f"Grid shape: {dem_data.elevation.shape}")
```

## API Reference

### `get_dem_loader() -> MeritDEMLoader`
Returns the singleton loader instance.

### `MeritDEMLoader`

#### `get_elevation_at_point(lat, lon) -> Optional[float]`
Get elevation at a single coordinate. Returns `None` if unavailable.

#### `get_elevation_window(bounds) -> DEMData`
Get elevation grid for a bounding box.
- `bounds`: Tuple of (west, south, east, north) in degrees
- Returns `DEMData` with `.elevation` (numpy array) and `.metadata`

#### `list_cached_tiles() -> List[str]`
List all locally cached tile filenames.

#### `clear_cache()`
Delete all cached tiles.

## Configuration

Set in `app/config.py` or `.env`:

```env
DEM_DATA_DIR=../data/elevation/merit  # Tile cache directory
```

## Tile Naming

Tiles are named `merit_{lat}_{lon}.tif` where lat/lon are integer floor values.

Example: Point (51.178, -115.570) uses tile `merit_51_-116.tif`

## Data Source

[NASA SRTM v3 1-arcsecond](https://data.naturalcapitalalliance.stanford.edu/) (~30m resolution)
