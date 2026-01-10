# Data Integration Guide

This guide explains how to integrate real terrain, elevation, and OpenStreetMap data into Beacon.ai.

## Overview

The system now supports loading real data from multiple sources:
- **Elevation data**: GeoTIFF files (SRTM, PDEM, etc.)
- **Trail/Road networks**: OpenStreetMap JSON (Overpass API format)
- **Weather conditions**: Open-Meteo API (automatic)

If real data is unavailable, the system **automatically falls back to synthetic data** for testing.

## Quick Start (No Setup Required)

The system works out of the box with synthetic data. No additional setup is needed for basic testing.

## Adding Real Elevation Data

### Option 1: Download SRTM Data (Free, Global Coverage)

1. Visit [SRTM Data](https://srtm.csi.cgiar.org/)
2. Download tiles for your area of interest
3. Extract `.tif` files to `data/elevation/`

```bash
cd /Users/lucas/projects/beacon-ai
mkdir -p data/elevation
# Place your .tif files here
```

### Option 2: Use Elevation API (No Download)

The system can fetch elevation data from Open-Elevation API automatically. This is slower but requires no setup.

### Option 3: Provincial/Regional Data

For Ontario (example):
- Download PDEM (Provincial Digital Elevation Model) from Ontario GeoHub
- Convert to GeoTIFF format if needed
- Place in `data/elevation/`

### Installing GeoTIFF Support

To read GeoTIFF files, install optional dependencies:

```bash
# macOS
brew install gdal
cd /Users/lucas/projects/beacon-ai/backend
source venv/bin/activate
pip install rasterio

# Linux (Ubuntu/Debian)
sudo apt-get install gdal-bin libgdal-dev
pip install rasterio
```

## Adding OpenStreetMap Data

### Option 1: Download via Overpass API

Use the provided script or download manually:

```bash
# Example: Toronto area
curl -X POST "https://overpass-api.de/api/interpreter" \
  -d @- << 'EOF' > data/osm/toronto_trails.json
[out:json];
(
  way["highway"~"path|footway|track|bridleway"](43.5,-79.5,43.8,-79.2);
  way["highway"](43.5,-79.5,43.8,-79.2);
  way["waterway"](43.5,-79.5,43.8,-79.2);
  way["natural"="water"](43.5,-79.5,43.8,-79.2);
);
out geom;
EOF
```

Replace coordinates with your area: `(min_lat,min_lon,max_lat,max_lon)`

### Option 2: Use OSM Export Tools

1. Visit [OpenStreetMap Export](https://www.openstreetmap.org/export)
2. Select your area
3. Choose "Overpass API" format
4. Save JSON to `data/osm/`

### Option 3: Automatic Fetch (Coming Soon)

The system will automatically fetch OSM data for prediction areas if enabled.

## Data Directory Structure

```
data/
├── elevation/
│   ├── N43W080.tif        # SRTM tile
│   ├── ontario_pdem.tif   # Provincial data
│   └── .gitkeep
├── osm/
│   ├── toronto_trails.json
│   ├── area_roads.json
│   └── .gitkeep
├── weather_sample/
│   └── .gitkeep           # Weather is fetched live
└── SAR_manuals/
    └── .gitkeep
```

## Testing Your Data Integration

### Check Elevation Data

```python
from app.utils.elevation_loader import ElevationLoader

loader = ElevationLoader()
loader.load_geotiff("N43W080.tif")
elevation = loader.get_elevation(43.65, -79.38)
print(f"Elevation: {elevation}m")
```

### Check OSM Data

```python
from app.utils.osm_loader import OSMLoader

loader = OSMLoader()
loader.load_from_json("toronto_trails.json")
print(f"Loaded {len(loader.trails)} trails")
print(f"Loaded {len(loader.roads)} roads")
```

### Check Weather API

```python
from app.utils.weather_client import WeatherClient

client = WeatherClient()
weather = await client.get_weather(43.65, -79.38)
print(weather)
```

## How the System Uses Data

### Elevation
- Calculates slope for movement difficulty
- Influences uphill/downhill movement preferences
- Used in Tobler's Hiking Function

### Trails/Roads
- Strong attraction factor (3-5x probability)
- 90%+ of lost persons found within 500m of trails
- Higher movement speed on established paths

### Water Features
- Moderate attraction (people seek water)
- Used for navigation (following drainages)
- Survival factor after 12+ hours

### Weather
- Reduces movement speed in harsh conditions
- Increases exhaustion rate
- Forces sheltering in extreme weather
- Affects visibility and decision-making

## Performance Notes

- **Caching**: Terrain data is cached after first load
- **File Size**: Large GeoTIFF files (>100MB) may slow initial load
- **Resolution**: Match grid resolution to data resolution for best results
- **Coverage**: System works with partial data (e.g., elevation only)

## Troubleshooting

### "No module named 'rasterio'"
Install optional dependencies: `pip install rasterio`

### "GDAL not found"
Install system GDAL first: `brew install gdal` (macOS) or `apt-get install gdal-bin` (Linux)

### Data Not Loading
Check file paths are correct and files exist. System will silently fall back to synthetic data.

### Slow Performance
- Use smaller GeoTIFF files
- Reduce grid resolution (increase `grid_resolution_m`)
- Limit search radius

## Data Sources

### Recommended Sources

**Elevation:**
- [SRTM 90m Digital Elevation Database](https://srtm.csi.cgiar.org/) - Free, global
- [USGS Earth Explorer](https://earthexplorer.usgs.gov/) - US high-res
- Provincial GIS services - Regional high-res

**Trails/Roads:**
- [OpenStreetMap](https://www.openstreetmap.org/) - Free, global
- [Overpass Turbo](https://overpass-turbo.eu/) - Interactive OSM queries
- Regional trail networks (OTN for Ontario, etc.)

**Weather:**
- [Open-Meteo](https://open-meteo.com/) - Free, no API key (used automatically)

## Next Steps

1. Start with synthetic data (works now)
2. Add elevation data for your test area
3. Add OSM data for trails/roads
4. Weather is automatic (no setup needed)

The system is designed to work at any level of data integration - from completely synthetic to fully real data.
