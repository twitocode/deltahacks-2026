"""
Test script with sample frontend input data.

This test sends a request to the backend API matching what the frontend sends:
POST /api/v1/search with SearchRequest payload.

Run with: python -m tests.test_frontend_sample (from backend directory)
"""

import asyncio
import httpx
from datetime import datetime, timedelta


# Sample data format matching frontend MapPage.tsx
SAMPLE_FRONTEND_REQUEST = {
    "created_at": datetime.utcnow().isoformat() + "Z",
    "latitude": 51.1784,  # Banff, Alberta
    "longitude": -115.5708,
    "time_last_seen": (datetime.utcnow() - timedelta(hours=3)).isoformat() + "Z",
    "age": "35",
    "gender": "male",
    "skill_level": 3  # Intermediate
}


async def test_search_endpoint():
    """Test the /api/v1/search endpoint with sample frontend data."""
    
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("Frontend Sample Request Test")
    print("=" * 60)
    print(f"\nTest Payload:")
    for key, value in SAMPLE_FRONTEND_REQUEST.items():
        print(f"  {key}: {value}")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            print(f"\n[*] Sending POST to {base_url}/api/v1/search...")
            
            response = await client.post(
                f"{base_url}/api/v1/search",
                json=SAMPLE_FRONTEND_REQUEST
            )
            
            print(f"[*] Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Analyze response structure
                print(f"\n[✓] SUCCESS! Response received.")
                print(f"[*] Response keys: {list(data.keys())}")
                
                # Extract metadata
                if 'metadata' in data:
                    metadata = data['metadata']
                    print(f"\n[*] Grid Info:")
                    print(f"    Width: {metadata.get('grid_width')}")
                    print(f"    Height: {metadata.get('grid_height')}")
                    print(f"    Cell Size: {metadata.get('cell_size_meters')}m")
                    print(f"    Origin: {metadata.get('origin')}")
                
                # Extract predictions
                predictions = data.get('predictions', {})
                print(f"\n[*] Predictions contains {len(predictions)} time slices")
                
                if predictions:
                    # Show available time slices
                    time_keys = list(predictions.keys())
                    print(f"[*] Available time slices: {time_keys}")
                    
                    # Show first time slice info
                    first_key = time_keys[0]
                    first_grid = predictions[first_key]
                    
                    if first_grid and isinstance(first_grid, list):
                        print(f"\n[*] Sample Time Slice (t={first_key} hours):")
                        print(f"    Grid shape: {len(first_grid)} x {len(first_grid[0]) if first_grid else 0}")
                        
                        # Find max probability cell
                        max_prob = 0
                        max_row, max_col = 0, 0
                        for i, row in enumerate(first_grid):
                            for j, val in enumerate(row):
                                if val > max_prob:
                                    max_prob = val
                                    max_row, max_col = i, j
                        
                        print(f"    Max probability: {max_prob:.4f} at cell ({max_row}, {max_col})")
                    
                return True
            else:
                print(f"\n[✗] FAILED! Status: {response.status_code}")
                print(f"    Response: {response.text}")
                return False
                
        except httpx.ConnectError:
            print("\n[✗] Connection Error - Is the backend server running?")
            print("    Start it with: cd backend && python -m app.main")
            return False
        except Exception as e:
            print(f"\n[✗] Error: {e}")
            return False


def main():
    """Run the async test."""
    success = asyncio.run(test_search_endpoint())
    print("\n" + "=" * 60)
    print(f"Test Result: {'PASSED' if success else 'FAILED'}")
    print("=" * 60)
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
