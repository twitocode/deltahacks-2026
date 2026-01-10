# Frontend Integration Guide

## Backend Status: ✅ Ready

The backend is **fully functional** and ready for frontend integration. All APIs work end-to-end.

---

## What the Frontend Needs to Send

### Minimum Required Input (from user form)

```javascript
{
  "last_known_location": {
    "latitude": 51.1784,      // Where they were last seen
    "longitude": -115.5708
  },
  "time_last_seen": "2026-01-10T20:00:00Z",  // ISO 8601 format
  "subject_profile": {
    "age": 28,                // Number
    "sex": "male",            // "male" or "female"
    "experience_level": "medium"  // "low", "medium", "high", or "expert"
  },
  "search_radius_km": 5.0,    // Optional, default 5.0
  "grid_resolution_m": 100.0  // Optional, default 100.0
}
```

### Example Form Fields

```html
<form id="predictionForm">
  <!-- Location -->
  <input type="number" step="any" name="latitude" placeholder="Latitude" required>
  <input type="number" step="any" name="longitude" placeholder="Longitude" required>
  
  <!-- Time -->
  <input type="datetime-local" name="time_last_seen" required>
  
  <!-- Subject Profile -->
  <input type="number" name="age" min="1" max="120" required>
  <select name="sex" required>
    <option value="male">Male</option>
    <option value="female">Female</option>
  </select>
  <select name="experience_level" required>
    <option value="low">Low (Novice)</option>
    <option value="medium">Medium (Intermediate)</option>
    <option value="high">High (Advanced)</option>
    <option value="expert">Expert</option>
  </select>
  
  <!-- Advanced (Optional) -->
  <input type="number" name="search_radius_km" value="5.0" step="0.1">
  <input type="number" name="grid_resolution_m" value="100" step="10">
  
  <button type="submit">Generate Prediction</button>
</form>
```

---

## What the Backend Returns

### Full Response Structure

```javascript
{
  "request_id": "abc123...",
  "snapshots": [
    {
      "timestamp": "2026-01-10T20:00:00Z",
      "hours_elapsed": 0.0,
      "max_probability": 1.0,
      "mean_probability": 0.0001,
      "grid_cells": [
        {
          "latitude": 51.1784,
          "longitude": -115.5708,
          "probability": 1.0,
          "elevation": 1463.2
        },
        // ... more cells (sorted by probability descending)
      ]
    },
    // ... more snapshots (every 15 minutes)
  ],
  "metadata": {
    "grid_size": 100,
    "grid_resolution_m": 100.0,
    "search_radius_km": 5.0,
    "total_snapshots": 49,
    "subject_age": 28,
    "subject_experience": "medium",
    "weather_conditions": "15.2°C, clear",     // ✅ Real weather
    "weather_impact": "1.00x movement speed"   // ✅ Weather effect
  }
}
```

---

## Simple Frontend Example

### Option 1: REST API (Simple)

```javascript
async function getPrediction(formData) {
  const request = {
    last_known_location: {
      latitude: parseFloat(formData.latitude),
      longitude: parseFloat(formData.longitude)
    },
    time_last_seen: new Date(formData.time_last_seen).toISOString(),
    subject_profile: {
      age: parseInt(formData.age),
      sex: formData.sex,
      experience_level: formData.experience_level
    },
    search_radius_km: parseFloat(formData.search_radius_km) || 5.0,
    grid_resolution_m: parseFloat(formData.grid_resolution_m) || 100.0
  };
  
  const response = await fetch('http://localhost:8000/api/v1/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  });
  
  return await response.json();
}

// Use it
const prediction = await getPrediction(formData);
console.log('Weather:', prediction.metadata.weather_conditions);

// Display on map
prediction.snapshots.forEach(snapshot => {
  snapshot.grid_cells.forEach(cell => {
    addHeatmapPoint(cell.latitude, cell.longitude, cell.probability);
  });
});
```

### Option 2: WebSocket (Progressive)

```javascript
function streamPrediction(formData) {
  const ws = new WebSocket('ws://localhost:8000/ws/predict');
  
  ws.onopen = () => {
    const request = {
      last_known_location: {
        latitude: parseFloat(formData.latitude),
        longitude: parseFloat(formData.longitude)
      },
      time_last_seen: new Date(formData.time_last_seen).toISOString(),
      subject_profile: {
        age: parseInt(formData.age),
        sex: formData.sex,
        experience_level: formData.experience_level
      },
      search_radius_km: parseFloat(formData.search_radius_km) || 5.0,
      grid_resolution_m: parseFloat(formData.grid_resolution_m) || 100.0
    };
    
    ws.send(JSON.stringify(request));
  };
  
  ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    
    switch(message.type) {
      case 'started':
        console.log('Prediction started');
        break;
      
      case 'progress':
        updateProgressBar(message.progress);
        console.log(message.message);
        break;
      
      case 'snapshot':
        // Render snapshot immediately
        updateMap(message.data);
        break;
      
      case 'completed':
        console.log('Prediction complete');
        break;
      
      case 'error':
        console.error(message.message);
        break;
    }
  };
}
```

---

## What Works Automatically

### ✅ Weather API Integration
- **Fetches automatically** when you submit location
- **No API key needed** (uses Open-Meteo free tier)
- Returns in `metadata.weather_conditions`
- Affects movement predictions

### ✅ Age/Sex Behavioral Models
- Different movement speeds by age
- Gender-based behavior patterns
- Experience level adjustments
- All research-backed parameters

### ✅ Terrain Simulation
- Currently uses **synthetic elevation** (works anywhere)
- Automatically uses **real data** if you add files to `data/` dirs
- No code changes needed

### ✅ Time-Series Predictions
- Snapshots every 15 minutes
- From "time_last_seen" to +12 hours
- Probability evolution over time

---

## Testing Without Frontend

### Test with curl
```bash
cd backend
./test_full_simulation.sh
```

Or manual curl:
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "last_known_location": {"latitude": 51.1784, "longitude": -115.5708},
    "time_last_seen": "2026-01-10T20:00:00Z",
    "subject_profile": {"age": 28, "sex": "male", "experience_level": "medium"},
    "search_radius_km": 5.0,
    "grid_resolution_m": 100.0
  }'
```

### Test with Python
```bash
cd backend
source venv/bin/activate
python test_api.py
```

---

## Map Visualization Tips

### Displaying Probability Heatmap

```javascript
import L from 'leaflet';
import 'leaflet.heat';

// Create heatmap layer
const heatmapData = snapshot.grid_cells.map(cell => [
  cell.latitude,
  cell.longitude,
  cell.probability  // Intensity
]);

const heat = L.heatLayer(heatmapData, {
  radius: 25,
  blur: 15,
  maxZoom: 17,
  max: 1.0  // Max probability
}).addTo(map);
```

### Time Slider

```javascript
const [timeIndex, setTimeIndex] = useState(0);
const currentSnapshot = prediction.snapshots[timeIndex];

<input 
  type="range" 
  min="0" 
  max={prediction.snapshots.length - 1}
  value={timeIndex}
  onChange={(e) => setTimeIndex(Number(e.target.value))}
/>
<span>{currentSnapshot.timestamp}</span>
```

---

## Error Handling

```javascript
try {
  const response = await fetch('http://localhost:8000/api/v1/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Prediction failed');
  }
  
  return await response.json();
  
} catch (error) {
  console.error('Prediction error:', error);
  alert(`Error: ${error.message}`);
}
```

---

## Next Steps for Frontend

1. **Create form** with location, time, age, sex inputs
2. **Call REST API** with form data
3. **Display heatmap** using Leaflet.heat or similar
4. **Add time slider** to show evolution
5. **Show weather** from metadata
6. **(Optional)** Switch to WebSocket for progressive rendering

---

## Testing Locations

### Banff National Park (Canada)
```javascript
{ latitude: 51.1784, longitude: -115.5708 }
```

### Yosemite Valley (USA)
```javascript
{ latitude: 37.7456, longitude: -119.5937 }
```

### Toronto Area (Canada)
```javascript
{ latitude: 43.6532, longitude: -79.3832 }
```

---

## API Documentation

Interactive API docs available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Summary

**YES** - The simulation runs perfectly with all APIs when given:
- ✅ Location (lat/lon)
- ✅ Time (ISO 8601 string)
- ✅ Age (number)
- ✅ Sex (male/female)

**What happens automatically:**
- ✅ Weather fetched from Open-Meteo
- ✅ Age/sex behavioral model applied
- ✅ Terrain simulation (synthetic or real)
- ✅ Time-series predictions generated
- ✅ Weather impact calculated
- ✅ Full response with all data

**Frontend just needs to:**
1. Collect user input
2. POST to `/api/v1/predict`
3. Display results on map

That's it! 🚀
