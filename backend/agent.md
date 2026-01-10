# Beacon.ai - Agent Development Notes

## Project Overview
Beacon.ai is a Search and Rescue (SAR) prediction system designed to help emergency response teams locate missing persons in wilderness areas using probabilistic modeling and behavioral analysis.

## Current Status ✅

### Completed
- ✅ **Core Backend Architecture**
  - FastAPI REST API with CORS support
  - Pydantic schemas for type-safe data validation
  - Modular structure (routes, models, services, utils)

- ✅ **Prediction Engine** (`app/services/prediction_engine.py`)
  - Grid-based probability simulation
  - Time-series snapshots (15-minute intervals)
  - Probability distribution evolution algorithm
  - Synthetic terrain generation for testing

- ✅ **Human Behavior Model** (`app/models/human_behavior.py`)
  - Age/sex-based travel rates
  - Movement strategies (route traveling, backtracking, staying put, etc.)
  - Time-dependent behavioral changes (panic → exhaustion → shelter-seeking)
  - Tobler's Hiking Function for terrain difficulty
  - Panic multipliers over time

- ✅ **Terrain Model** (`app/models/terrain_model.py`)
  - Grid coordinate system (lat/lon ↔ grid conversion)
  - Elevation tracking
  - Trail/road attraction calculations
  - Water feature attraction
  - Slope calculation
  - Vegetation density support

- ✅ **API Endpoints**
  - `POST /api/v1/predict` - Generate predictions
  - `GET /health` - Health check
  - `GET /` - API info
  - Interactive docs at `/docs`

- ✅ **Testing Infrastructure**
  - Test script (`test_api.py`) for validation
  - Virtual environment setup
  - Dependencies installed and working

- ✅ **Server Running**
  - FastAPI server successfully starts
  - Runs on http://localhost:8000
  - CORS enabled for frontend integration

## Next Steps 🚀

### High Priority
1. **Real Terrain Data Integration**
   - Load actual elevation data from PDEM
   - Parse OpenStreetMap trail/road data
   - Integrate water feature data
   - Cache terrain data for performance

2. **Frontend Development**
   - React + Vite setup
   - Map integration (Mapbox or Leaflet)
   - Heatmap overlay visualization
   - Time slider for snapshot navigation
   - Input form for prediction requests

3. **WebSocket Support**
   - Real-time streaming of prediction snapshots
   - Progress updates during calculation
   - Reduce perceived latency

### Medium Priority
4. **Weather Integration**
   - Open-Meteo API client
   - Weather impact on movement (temperature, precipitation, wind)
   - Time-of-day considerations (daylight/darkness)

5. **Performance Optimization**
   - Vectorize grid operations with NumPy
   - Implement probability threshold cutoffs
   - Cache expensive calculations
   - Consider numba JIT compilation for hot paths

6. **Data Loading Utilities** (`app/utils/`)
   - OSM data parser
   - Elevation data loader
   - Trail network graph builder (NetworkX)
   - Weather API client

### Lower Priority
7. **Historical Validation**
   - Load ISRID case data
   - Compare predictions to actual outcomes
   - Tune behavioral parameters

8. **Advanced Features**
   - Multiple agent simulation
   - Terrain impassability (cliffs, rivers)
   - Search team coordination suggestions
   - Export to KML for GPS devices

## Technical Architecture

### Algorithm Flow
```
1. Input: LKL, time last seen, subject profile
2. Initialize grid centered on LKL
3. Load terrain data (elevation, trails, water)
4. Set initial probability = 1.0 at LKL
5. For each 15-min interval:
   a. Get movement parameters (age, sex, experience, time)
   b. For each cell with probability:
      - Calculate reachable neighbors
      - Weight by terrain, behavior, distance
      - Distribute probability
   c. Normalize grid
   d. Create snapshot
6. Return all snapshots to frontend
```

### Key Design Decisions
- **Grid-based over agent-based**: More efficient for probability visualization
- **No ML/DL**: Insufficient training data; heuristic approach is validated by SAR research
- **15-minute intervals**: Balance between granularity and computation
- **Probability threshold (0.01%)**: Reduce data size while keeping meaningful predictions
- **Synthetic terrain for testing**: Allows development without data dependencies

## Data Sources

### Integrated
- None yet (using synthetic data)

### Planned
- **Elevation**: Provincial Digital Elevation Model (PDEM) - Ontario
- **Trails**: OpenStreetMap, Ontario Trail Network (OTN)
- **Weather**: Open-Meteo API
- **Validation**: ISRID (International Search & Rescue Incident Database)

## API Usage Example

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

## Key Files

```
beacon-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                      # FastAPI entry point
│   │   ├── routes/
│   │   │   ├── prediction.py            # Prediction endpoints
│   │   │   └── status.py                # Health check
│   │   ├── models/
│   │   │   ├── schemas.py               # Pydantic models
│   │   │   ├── human_behavior.py        # Behavioral patterns
│   │   │   └── terrain_model.py         # Terrain grid system
│   │   ├── services/
│   │   │   └── prediction_engine.py     # Core algorithm
│   │   └── utils/                       # (empty, for data loaders)
│   ├── requirements.txt                 # Dependencies
│   ├── test_api.py                      # API test script
│   ├── tests/                           # (empty, for unit tests)
│   └── venv/                            # Virtual environment (gitignored)
├── data/                                # Data directories (gitignored contents)
│   ├── osm/                             # OpenStreetMap trail data
│   ├── elevation/                       # Elevation datasets
│   ├── weather_sample/                  # Weather data cache
│   └── SAR_manuals/                     # SAR research documents
├── .gitignore                           # Git ignore rules
├── README.md                            # Project documentation
└── agent.md                             # This file
```

## Development Commands

```bash
# Start backend server
cd /Users/lucas/projects/beacon-ai/backend
source venv/bin/activate
python -m app.main

# Test API
python test_api.py

# Install new dependencies
pip install <package>
pip freeze > requirements.txt
```

## Known Issues & TODOs

### Bugs
- None identified yet (synthetic data only)

### Performance
- Grid iteration in `_evolve_probability` is O(n²) - could vectorize
- Large grids (small resolution) may be slow
- No caching of terrain calculations

### Code Quality
- TODO comments for data loading in `prediction_engine.py`
- Missing docstring details in some methods
- No unit tests yet

## Research References

### SAR Behavioral Data
- Lost person behavior varies by demographic (age, sex, experience)
- 90%+ found within 500m of trails/roads
- Panic stages: Separation → Isolation → Realization
- Modern hikers go uphill (cell signal) vs. traditional downhill (water)

### Algorithms
- **Tobler's Hiking Function**: Walking speed vs. slope
- **Distance decay**: Exponential probability falloff from LKL
- **Dispersion angle**: Cone-based probability if direction known

### Data Sources
- ISRID: Statistical patterns from real cases
- SARBayes: Open-source Bayesian SAR probability mapping

## Notes for Future Developers

1. **Grid Resolution**: 100m is a good default. Smaller = more accurate but slower
2. **Trail Attraction**: Currently 3x multiplier - tune based on validation data
3. **Panic Multiplier**: Early hours increase speed by 30% - research-backed
4. **Staying Put Weight**: Increases to 50% after 12 hours - most successful strategy
5. **Time Horizon**: Current +12 hours, could extend to 72 hours for long searches

## Hackathon Context

This project was developed for a hackathon focused on emergency services and AI/Edge computing. The core innovation is making SAR prediction accessible via a simple web interface, democratizing tools that were previously manual or proprietary.

### Demo Strategy
1. Show map interface with input form
2. Submit prediction for a test location (e.g., Toronto-area park)
3. Animate heatmap evolution over time
4. Highlight top probability zones for search prioritization
5. Emphasize: "Decision support, not autonomous rescue"

---

**Last Updated**: 2026-01-10  
**Status**: Backend operational, ready for frontend integration and real data
