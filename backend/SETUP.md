# Beacon.ai - Quick Setup Guide

## Prerequisites
- Python 3.9+ installed
- macOS, Linux, or Windows with WSL

## Installation

### 1. Clone or navigate to the project
```bash
cd /Users/lucas/projects/beacon-ai
```

### 2. Start the backend
```bash
cd backend
./start.sh
```

That's it! The script will:
- Check for virtual environment (create if needed)
- Install dependencies
- Start the FastAPI server

## Access Points

Once running, you can access:

- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **Health Check**: http://localhost:8000/health
- **ReDoc**: http://localhost:8000/redoc

## Testing the API

### Option 1: Use the test script
```bash
cd backend
source venv/bin/activate
python test_api.py
```

### Option 2: Use curl
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
    "search_radius_km": 3.0,
    "grid_resolution_m": 150.0
  }'
```

### Option 3: Use the interactive docs
Visit http://localhost:8000/docs and use the "Try it out" feature.

## Project Structure

```
beacon-ai/
├── backend/           # FastAPI backend
│   ├── app/          # Application code
│   ├── start.sh      # Quick start script
│   └── test_api.py   # Test script
├── data/             # Data directories (empty)
├── README.md         # Full documentation
├── agent.md          # Development notes
└── .gitignore        # Git ignore rules
```

## What's Included

✅ **Core Prediction Engine**
- Grid-based probability simulation
- Behavioral modeling (age, sex, experience)
- Terrain-aware movement
- Time-series predictions (15-min intervals)

✅ **REST API**
- POST /api/v1/predict - Generate predictions
- GET /health - Health check
- Full OpenAPI/Swagger documentation

✅ **Testing**
- Synthetic terrain for development
- API test script included

## What's Next

The backend is fully operational with synthetic data. Next steps:

1. **Frontend Development** - Map visualization with React
2. **Real Data Integration** - Load actual terrain/elevation data
3. **Weather API** - Integrate Open-Meteo for environmental factors
4. **WebSocket Support** - Real-time prediction streaming

## Troubleshooting

### Port 8000 already in use
```bash
# Find process using port 8000
lsof -ti:8000 | xargs kill -9

# Or change port in backend/app/main.py
```

### Virtual environment issues
```bash
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Import errors
Make sure you're in the backend directory and the virtual environment is activated:
```bash
cd backend
source venv/bin/activate
python -m app.main
```

## Support

For detailed documentation, see:
- **README.md** - Full project documentation
- **agent.md** - Development notes and architecture
- **/docs endpoint** - Interactive API documentation

---

**Built for SAR teams. Every minute counts. 🚁**
