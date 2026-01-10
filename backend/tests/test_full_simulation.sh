#!/bin/bash
# Test that simulation works end-to-end with all APIs

echo "🧪 Testing Full Simulation (Location + Time + Age + Sex)"
echo "========================================================="
echo ""

# Banff National Park test case
echo "📍 Location: Banff, Alberta"
echo "⏰ Time: 2 hours ago"
echo "👤 Subject: 28 year old male, medium experience"
echo ""
echo "Making API request..."
echo ""

curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "last_known_location": {
      "latitude": 51.1784,
      "longitude": -115.5708
    },
    "time_last_seen": "2026-01-10T20:00:00Z",
    "subject_profile": {
      "age": 28,
      "sex": "male",
      "experience_level": "medium"
    },
    "search_radius_km": 5.0,
    "grid_resolution_m": 150.0
  }' 2>/dev/null | python3 -m json.tool | head -50

echo ""
echo "✅ If you see JSON output above, the simulation is working!"
echo ""
echo "📊 Full response includes:"
echo "  - Weather conditions (from Open-Meteo API)"
echo "  - Movement predictions (age/sex behavioral model)"
echo "  - Time-series snapshots (every 15 minutes)"
echo "  - Probability grid (lat/lon/elevation)"
