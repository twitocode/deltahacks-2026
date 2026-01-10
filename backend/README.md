# Beacon.ai - SAR Prediction System

**Search and Rescue prediction system for locating missing persons in wilderness areas**

## Problem

Search & Rescue teams face critical challenges when locating missing persons in forested and wilderness areas:
- Limited information (last known location, time, subject profile)
- Vast search areas with limited daylight and resources
- Need to prioritize search zones efficiently

## Solution

Beacon.ai uses probabilistic modeling to predict the most likely locations of missing persons over time, combining:
- **Human Behavior Patterns**: Age, experience, panic stages, exhaustion
- **Terrain Analysis**: Elevation, slope, vegetation density
- **Environmental Attractors**: Trails, roads, water sources
- **Time-Based Evolution**: Movement patterns change from panic → exhaustion → shelter-seeking

## Features

- Real-time probability heatmap generation
- Time-series predictions (from last seen to +12 hours)
- 15-minute interval snapshots
- Terrain-aware movement simulation
- Experience-based behavioral modeling
- REST API for integration

## Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI** - High-performance API framework
- **NumPy/SciPy** - Numerical computation for probability simulation
- **Pydantic** - Data validation
- **NetworkX** - Graph-based trail analysis (planned)

### Frontend (Planned)
- React + Vite
- TanStack Query
- TailwindCSS
- Mapbox/Leaflet for interactive maps

## Project Structure

```
beacon-ai/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── routes/              # API endpoints
│   │   ├── models/              # Pydantic schemas & behavioral models
│   │   ├── services/            # Core prediction engine
│   │   └── utils/               # Data loading utilities
│   ├── requirements.txt
│   ├── start.sh                 # Quick start script
│   └── test_api.py              # API test script
├── data/                        # Terrain, elevation, trail data (gitignored)
│   ├── osm/
│   ├── elevation/
│   ├── weather_sample/
│   └── SAR_manuals/
├── .gitignore
├── README.md
└── agent.md                     # Development notes
```

## Quick Start

### Backend Setup

**Option 1: Quick Start (Recommended)**
```bash
cd /Users/lucas/projects/beacon-ai/backend
./start.sh
```

**Option 2: Manual Setup**
```bash
cd /Users/lucas/projects/beacon-ai/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python -m app.main
```

The API will be available at:
- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### API Usage

**Example Prediction Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "last_known_location": {
      "latitude": 43.6532,
      "longitude": -79.3832
    },
    "time_last_seen": "2026-01-10T18:00:00Z",
    "subject_profile": {
      "age": 28,
      "sex": "male",
      "experience_level": "medium"
    },
    "search_radius_km": 5.0,
    "grid_resolution_m": 100.0
  }'
```

**Response:**
- Array of time snapshots (every 15 minutes)
- Each snapshot contains grid cells with probability values
- Includes lat/lon coordinates and elevation for each cell

## Algorithm Overview

### Movement Simulation
1. **Grid-Based Approach**: Divides search area into cells (default 100m²)
2. **Probability Distribution**: Starts at 100% at last known location
3. **Time Evolution**: Each 15-min interval, probability spreads based on:
   - Travel distance (age/sex-dependent base rates)
   - Terrain difficulty (Tobler's Hiking Function for slope)
   - Behavioral strategies (route traveling, downhill seeking, staying put, etc.)
   - Panic/exhaustion modifiers over time

### Key Behavioral Factors
- **0-3 hours**: High panic, erratic movement, uphill seeking (cell signal)
- **3-12 hours**: Exhaustion setting in, more rational decisions
- **12+ hours**: Severe exhaustion, shelter-seeking, staying put

### Terrain Weighting
- **Trails/Roads**: 3-5x attraction factor (90%+ found within 500m)
- **Slope**: Steep uphill heavily penalized unless experienced
- **Vegetation**: Dense brush reduces movement probability
- **Water**: Moderate attraction factor

## Data Sources (Planned Integration)

- **OpenStreetMap**: Trail and road networks
- **Provincial Digital Elevation Model (PDEM)**: Ontario elevation data
- **Open-Meteo API**: Weather conditions
- **Ontario Trail Network (OTN)**: Official trail data
- **ISRID**: International Search & Rescue Incident Database for validation

## Development Roadmap

- [x] Core prediction engine
- [x] REST API with FastAPI
- [x] Behavioral modeling
- [x] Terrain simulation
- [ ] WebSocket support for real-time updates
- [ ] Real terrain data integration (elevation, trails)
- [ ] Weather API integration
- [ ] Frontend map interface
- [ ] Historical case validation
- [ ] Mobile optimization

## Testing

```bash
# Run tests (once implemented)
pytest backend/tests/
```

## Contributing

This is a hackathon project. Contributions welcome!

## License

MIT License

## Acknowledgments

- SAR research and lost person behavior studies
- ISRID database for statistical patterns
- Open data providers (OSM, provincial GIS services)

---

**Built for emergency responders who save lives. 🚁🏔️**
