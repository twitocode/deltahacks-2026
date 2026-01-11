# Beacon.ai SAR Prediction Backend

The backend service for the Search and Rescue (SAR) probability prediction system. It utilizes Monte Carlo simulations, high-resolution elevation data (DEM), and OpenStreetMap features to predict the location of missing hikers.

## 🚀 Key Features

- **Monte Carlo Simulation**: Runs 1000+ autonomous agents with complex hiking behaviors (ISRID-based strategies).
- **Parallel Processing**: Scalable agent execution using Python multiprocessing.
- **Terrain Analysis**: Real-time DEM loading (Merit/SRTM) and resampling.
- **OSM Integration**: Fetches signals from trails, roads, and rivers via Overpass API.
- **Performance Profiling**: Granular timing logs for critical operations.

## 🛠️ Tech Stack

- **Framework**: FastAPI (Python 3.10+)
- **Data Processing**: NumPy, SciPy, Rasterio, Shapely
- **Concurrency**: `asyncio` + `ProcessPoolExecutor`

## ⚙️ Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy the example environment file and adjust settings if needed (e.g., enable parallelization).
```bash
cp .env.example .env
```

**Key Settings:**
- `DEM_DATA_DIR`: Path to elevation files.
- `PARALLEL_AGENTS`: Set to `True` for better performance.
- `MAX_WORKERS`: Adjust based on CPU cores (default: 2).

### 3. Run the Server
```bash
# Development mode (auto-reload)
python -m app.main

# Or using Uvicorn directly
uvicorn app.main:app --reload
```

## 📚 API Endpoints

### `POST /api/v1/search`
Run a SAR simulation.
- **Body**: `{ "latitude": 49.0, "longitude": -120.0, ... }`
- **Returns**: Probability heatmaps for each hour.

### `GET /api/elevation`
Get elevation for a specific point.

### `POST /api/terrain`
Get terrain metadata and bounds for a region.

## 🧪 Testing

Run the parallel simulation test script to verify the system:
```bash
python scripts/test_parallel_sim.py
```

## 📊 Logging & Performance

The system includes detailed performance logging to help identify bottlenecks.
Look for `[PERF]` tags in the console output to see timing for:
- Terrain Loading
- OSM Fetching
- Simulation Execution
