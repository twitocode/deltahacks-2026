# Waypoint 🔦

**AI-Powered Search and Rescue Prediction System**

A Monte Carlo simulation platform that predicts the probable location of missing persons based on behavioral psychology, terrain analysis, and environmental factors.

![Waypoint](frontend/public/images/logo-ico.png)

## 🎯 Overview

Waypoint uses agent-based simulation informed by ISRID (International Search and Rescue Incident Database) research to generate probability heatmaps showing where a missing person is most likely to be found. The system considers:

- **Human Behavior Patterns** - Direction traveling, route following, random walking, view enhancing, staying put
- **Terrain Analysis** - Elevation, slope (Tobler's hiking function), trails, roads, water features
- **Environmental Factors** - Temperature, precipitation, wind speed
- **Personal Profile** - Age, gender, experience level

## 🏗️ Architecture

```
deltahacks-2026/
├── backend/               # Python FastAPI server
│   ├── app/
│   │   ├── simulation/   # Monte Carlo agent simulation
│   │   ├── dem/          # Digital Elevation Model loader
│   │   ├── terrain/      # Terrain analysis pipeline
│   │   └── routes/       # API endpoints
│   └── tests/
└── frontend/             # React + Vite application
    ├── src/
    │   ├── components/   # Heatmap, Loading animations
    │   └── pages/        # HomePage, MapPage
    └── public/
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Mapbox API key

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Add your API keys
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env      # Add VITE_MAPBOX_TOKEN
npm run dev
```

## 📊 Simulation Model

### Movement Strategies (ISRID Research)
| Strategy | Probability | Behavior |
|----------|-------------|----------|
| Direction Traveling | 55.9% | Maintains fixed heading |
| Route Traveling | 37.7% | Follows trails/roads |
| Random Walking | 5.5% | Random direction |
| View Enhancing | 0.6% | Seeks high ground |
| Staying Put | 0.3% | Stays near last known position |

### Speed Factors
- **Base Speed**: 1.317 m/s (male), 1.241 m/s (female)
- **Age Decay**: -0.012 m/s per decade after 25
- **Tobler's Function**: Slope-adjusted movement speed
- **Weather Penalty**: 8% reduction for rain/snow

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/search` | POST | Run prediction simulation |
| `/api/v1/predict` | POST | Detailed time-series prediction |
| `/api/v1/status` | GET | Server health check |

### Example Request
```json
{
  "latitude": 51.1784,
  "longitude": -115.5708,
  "age": 35,
  "gender": "male",
  "skill_level": 3,
  "time_last_seen": "2024-01-11T06:00:00Z"
}
```

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Python 3.11+** | Runs the Monte Carlo agent simulation with 500+ concurrent agents |
| **FastAPI** | Handles REST endpoints (`/search`, `/predict`) with async support for concurrent requests |
| **NumPy** | Manages 50×50 probability grids and agent position arrays for heatmap generation |
| **Rasterio** | Parses NASA SRTM GeoTIFF tiles to extract elevation at any lat/lon coordinate |
| **SciPy** | Applies `gaussian_filter` (σ=0.5) to smooth raw agent density into viewable heatmaps |
| **httpx** | Fetches real-time weather from Open-Meteo API and trail data from Overpass API |
| **tqdm** | Displays simulation progress bar during Monte Carlo timesteps |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18** | Renders the search form, time slider, and playback controls as reusable components |
| **Vite** | Hot-reloads frontend changes in <100ms during development |
| **Mapbox GL JS** | Displays interactive satellite/terrain map with probability heatmap overlay layer |
| **TanStack Query** | Caches API responses and handles loading/error states for prediction requests |
| **TypeScript** | Type-checks API response schemas (`ServerGridResponse`, `GridMetadata`) |

### Data Sources
| Source | Purpose |
|--------|---------|
| **NASA SRTM DEM** | Provides 30m-resolution elevation for Tobler's hiking function slope calculations |
| **Open-Meteo API** | Returns current temperature, wind speed, and precipitation for weather penalties |
| **OpenStreetMap** | Supplies trail/road geometries to weight agent movement toward linear features |


## 👥 Team

Built with ❤️ at DeltaHacks 2026

## 📄 License

MIT License