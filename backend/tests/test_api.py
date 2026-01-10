#!/usr/bin/env python3
"""
Quick test script for Beacon.ai API
"""

import requests
import json
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{API_BASE}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    return response.status_code == 200

def test_prediction():
    """Test prediction endpoint"""
    print("Testing prediction endpoint...")
    
    # Sample prediction request (Toronto area, 2 hours ago)
    time_last_seen = (datetime.utcnow() - timedelta(hours=2)).isoformat() + "Z"
    
    payload = {
        "last_known_location": {
            "latitude": 43.6532,
            "longitude": -79.3832
        },
        "time_last_seen": time_last_seen,
        "subject_profile": {
            "age": 28,
            "sex": "male",
            "experience_level": "medium"
        },
        "search_radius_km": 3.0,  # Smaller radius for faster testing
        "grid_resolution_m": 150.0  # Larger cells for faster testing
    }
    
    print(f"Request payload:\n{json.dumps(payload, indent=2)}\n")
    
    response = requests.post(
        f"{API_BASE}/api/v1/predict",
        json=payload,
        timeout=60
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Request ID: {data['request_id']}")
        print(f"Total snapshots: {len(data['snapshots'])}")
        print(f"Metadata: {json.dumps(data['metadata'], indent=2)}")
        
        # Show first and last snapshot info
        if data['snapshots']:
            first = data['snapshots'][0]
            last = data['snapshots'][-1]
            
            print(f"\nFirst snapshot (t={first['hours_elapsed']}h):")
            print(f"  - Cells with probability: {len(first['grid_cells'])}")
            print(f"  - Max probability: {first['max_probability']:.6f}")
            
            print(f"\nLast snapshot (t={last['hours_elapsed']}h):")
            print(f"  - Cells with probability: {len(last['grid_cells'])}")
            print(f"  - Max probability: {last['max_probability']:.6f}")
            
            if last['grid_cells']:
                print(f"\nTop 3 most likely cells at final time:")
                for i, cell in enumerate(last['grid_cells'][:3], 1):
                    print(f"  {i}. Lat: {cell['latitude']:.4f}, "
                          f"Lon: {cell['longitude']:.4f}, "
                          f"Prob: {cell['probability']:.4f}")
        
        return True
    else:
        print(f"Error: {response.text}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Beacon.ai API Test Suite")
    print("=" * 60 + "\n")
    
    try:
        # Test health
        health_ok = test_health()
        
        if health_ok:
            # Test prediction
            pred_ok = test_prediction()
            
            if pred_ok:
                print("\n✅ All tests passed!")
            else:
                print("\n❌ Prediction test failed")
        else:
            print("\n❌ Health check failed - is the server running?")
            print("Start server with: python -m app.main")
    
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to API")
        print("Make sure the server is running: python -m app.main")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
