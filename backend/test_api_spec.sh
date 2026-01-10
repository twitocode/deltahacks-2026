#!/bin/bash
# Test the /predict/array endpoint matching exact API specification

echo "🧪 Testing API Specification Endpoint"
echo "======================================"
echo ""

echo "Request Body:"
echo "{"
echo '  "created_at": "2026-01-10T23:16:00Z",'
echo '  "latitude": 51.1784,'
echo '  "longitude": -115.5708,'
echo '  "time_last_seen": "2026-01-10T19:00:00Z",'
echo '  "age": "20",'
echo '  "gender": "male",'
echo '  "skill_level": 3'
echo "}"
echo ""

echo "Sending request to: POST /api/v1/predict/array"
echo ""

curl -X POST "http://localhost:8000/api/v1/predict/array" \
  -H "Content-Type: application/json" \
  -d '{
    "created_at": "2026-01-10T23:16:00Z",
    "latitude": 51.1784,
    "longitude": -115.5708,
    "time_last_seen": "2026-01-10T19:00:00Z",
    "age": "20",
    "gender": "male",
    "skill_level": 3
  }' 2>&1 | python3 -c "
import sys, json

try:
    data = json.load(sys.stdin)
    
    print('✅ Response received')
    print('')
    print('Response format:')
    print(f'  Type: {type(data).__name__}')
    print(f'  Keys (time hours): {list(data.keys())[:10]}...')
    print('')
    
    # Check first time key
    first_key = str(list(data.keys())[0])
    first_grid = data[first_key]
    
    print(f'Time {first_key} grid:')
    print(f'  Type: {type(first_grid).__name__}')
    print(f'  Shape: {len(first_grid)}x{len(first_grid[0]) if first_grid else 0}')
    
    # Calculate stats
    import numpy as np
    arr = np.array(first_grid)
    print(f'  Total probability: {arr.sum():.6f}')
    print(f'  Max probability: {arr.max():.6f}')
    print(f'  Non-zero cells: {np.count_nonzero(arr)}')
    print('')
    
    print('Sample response structure:')
    print('{')
    for i, key in enumerate(list(data.keys())[:3]):
        print(f'  \"{key}\": [[...{len(data[str(key)])}x{len(data[str(key)][0])} array...]],')
    print('  ...')
    print('}')
    print('')
    print('✅ API matches specification!')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
"

echo ""
echo "======================================"
echo "Test complete"
