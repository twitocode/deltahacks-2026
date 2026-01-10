# API Changelog

## New Features (January 2026)

### 1. Weather Integration ☁️

The prediction API now automatically fetches and incorporates weather conditions.

**What Changed:**
- Predictions now factor in temperature, precipitation, and wind speed
- Movement speed is reduced in harsh weather conditions
- Severe weather can force subjects to shelter in place

**Response Metadata:**
```json
{
  "metadata": {
    "weather_conditions": "15.2°C, light rain, moderate wind",
    "weather_impact": "0.72x movement speed"
  }
}
```

**Impact on Predictions:**
- Clear weather: No impact (1.0x speed)
- Light rain/wind: Minor reduction (0.8-0.9x)
- Heavy rain or extreme temps: Significant reduction (0.5-0.7x)
- Extreme conditions: Forces sheltering (0.3x)

---

### 2. Real Terrain Data Support 🗺️

The system can now load real elevation and trail data.

**Supported Data Sources:**
- **Elevation**: GeoTIFF files (SRTM, PDEM, etc.)
- **Trails/Roads**: OpenStreetMap JSON (Overpass API format)
- **Weather**: Open-Meteo API (automatic)

**Automatic Fallback:**
If real data is unavailable, the system uses synthetic data for testing.

**How to Add Data:**
See [DATA_INTEGRATION.md](DATA_INTEGRATION.md) for detailed instructions.

---

### 3. WebSocket Streaming 🔴

New WebSocket endpoint for real-time prediction streaming.

**Endpoint:** `ws://localhost:8000/ws/predict`

**Why Use WebSockets:**
- Receive predictions as they're calculated
- Real-time progress updates
- Reduced perceived latency
- Better UX for long-running predictions

**Protocol:**
```javascript
// Connect
const ws = new WebSocket('ws://localhost:8000/ws/predict');

// Send prediction request
ws.onopen = () => {
  ws.send(JSON.stringify({
    last_known_location: { latitude: 43.65, longitude: -79.38 },
    time_last_seen: "2026-01-10T18:00:00Z",
    subject_profile: { age: 28, sex: "male", experience_level: "medium" },
    search_radius_km: 5.0,
    grid_resolution_m: 100.0
  }));
};

// Receive updates
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch(message.type) {
    case 'started':
      console.log('Prediction started');
      break;
    case 'progress':
      console.log(`Progress: ${message.progress * 100}%`);
      break;
    case 'snapshot':
      // Display snapshot on map
      updateMap(message.data);
      break;
    case 'completed':
      console.log('Prediction completed');
      break;
    case 'error':
      console.error(message.message);
      break;
  }
};
```

**Message Types:**
- `started`: Acknowledgment
- `progress`: Progress updates (0.0 to 1.0)
- `snapshot`: Individual time snapshot
- `completed`: All snapshots sent
- `error`: Error occurred

---

### 4. Terrain Caching ⚡

Automatic caching of terrain data for improved performance.

**Benefits:**
- Repeated predictions in same area are much faster
- Reduces data loading overhead
- Automatic cache management (max 50 locations)

**How It Works:**
- First prediction: Loads terrain data (~1-2 seconds)
- Subsequent predictions: Uses cached data (~instant)
- Cache key: Location rounded to 2 decimals + radius + resolution

**No Configuration Required:** Works automatically.

---

## API Endpoints

### Existing Endpoints

#### `POST /api/v1/predict`
Generate prediction (now with weather integration)

**Changes:**
- Now async (to support weather API)
- Returns weather info in metadata
- Faster with terrain caching

**Request:** (unchanged)
```json
{
  "last_known_location": { "latitude": 43.65, "longitude": -79.38 },
  "time_last_seen": "2026-01-10T18:00:00Z",
  "subject_profile": { "age": 28, "sex": "male", "experience_level": "medium" },
  "search_radius_km": 5.0,
  "grid_resolution_m": 100.0
}
```

**Response:** (new metadata fields)
```json
{
  "request_id": "...",
  "snapshots": [...],
  "metadata": {
    "grid_size": 100,
    "grid_resolution_m": 100.0,
    "search_radius_km": 5.0,
    "total_snapshots": 49,
    "subject_age": 28,
    "subject_experience": "medium",
    "weather_conditions": "15.2°C, clear",
    "weather_impact": "1.00x movement speed"
  }
}
```

#### `GET /health`
Health check (unchanged)

---

### New Endpoints

#### `WS /ws/predict`
WebSocket streaming predictions

See WebSocket section above for details.

#### `WS /ws/status`
WebSocket connection test

Simple echo endpoint for testing WebSocket connectivity.

---

## Breaking Changes

### None! 🎉

All changes are backward compatible. Existing API clients will continue to work without modification.

**New Features are Opt-in:**
- Weather integration: Automatic (no client changes needed)
- Real terrain data: Optional (falls back to synthetic)
- WebSocket streaming: Alternative endpoint (REST API still works)

---

## Performance Improvements

### Before
- First prediction: ~2-3 seconds
- Subsequent predictions: ~2-3 seconds
- No weather data
- Synthetic terrain only

### After
- First prediction: ~2-4 seconds (includes weather API call)
- Subsequent predictions (same area): ~0.5-1 second (cached terrain)
- Weather integration: ~200ms overhead
- Real terrain data: Available (optional)
- WebSocket streaming: Progressive rendering

**Overall:** 2-3x faster for repeated predictions in the same area.

---

## Migration Guide

### For Existing Clients

**No changes required!** The API is fully backward compatible.

**To take advantage of new features:**

1. **Weather Info:** Check `metadata.weather_conditions` in response
2. **WebSocket Streaming:** Optionally switch to WebSocket endpoint
3. **Real Data:** Add terrain files (see DATA_INTEGRATION.md)

### Example Update

**Before:**
```javascript
const response = await fetch('http://localhost:8000/api/v1/predict', {
  method: 'POST',
  body: JSON.stringify(request)
});
const prediction = await response.json();
displayPrediction(prediction);
```

**After (with weather info):**
```javascript
const response = await fetch('http://localhost:8000/api/v1/predict', {
  method: 'POST',
  body: JSON.stringify(request)
});
const prediction = await response.json();

// Show weather impact
console.log(`Weather: ${prediction.metadata.weather_conditions}`);
console.log(`Impact: ${prediction.metadata.weather_impact}`);

displayPrediction(prediction);
```

**After (with WebSocket streaming):**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/predict');
ws.onopen = () => ws.send(JSON.stringify(request));
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  if (message.type === 'snapshot') {
    displaySnapshotIncremental(message.data);
  }
};
```

---

## Testing New Features

### Test Weather Integration
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "last_known_location": {"latitude": 43.65, "longitude": -79.38},
    "time_last_seen": "2026-01-10T18:00:00Z",
    "subject_profile": {"age": 28, "sex": "male", "experience_level": "medium"},
    "search_radius_km": 3.0,
    "grid_resolution_m": 150.0
  }' | jq '.metadata.weather_conditions'
```

### Test WebSocket (using websocat)
```bash
# Install websocat: brew install websocat
echo '{"last_known_location":{"latitude":43.65,"longitude":-79.38},"time_last_seen":"2026-01-10T18:00:00Z","subject_profile":{"age":28,"sex":"male","experience_level":"medium"},"search_radius_km":3.0,"grid_resolution_m":150.0}' | \
  websocat ws://localhost:8000/ws/predict
```

### Test Terrain Caching
```bash
# First prediction (slower - loads terrain)
time curl -X POST "http://localhost:8000/api/v1/predict" -H "Content-Type: application/json" -d '...'

# Second prediction same location (faster - uses cache)
time curl -X POST "http://localhost:8000/api/v1/predict" -H "Content-Type: application/json" -d '...'
```

---

## Next Steps

1. **Try the new features** with existing code (no changes needed)
2. **Add real terrain data** for your area (see DATA_INTEGRATION.md)
3. **Switch to WebSocket** for progressive rendering (optional)
4. **Monitor weather impact** in metadata for extreme conditions

Questions? Check the interactive docs at http://localhost:8000/docs
