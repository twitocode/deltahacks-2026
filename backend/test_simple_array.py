"""
Test the simplified probability array endpoint with Banff scenario.

This tests the /predict/simple endpoint that returns only a 2D probability array.
Uses the same scenario as test_banff_case.py but with simplified output.

Scenario:
- Location: Banff, Alberta (51.1784° N, 115.5708° W)
- Subject: 20-year-old male, medium experience
- Last seen: 08:00 (4 hours ago)
- Current time: 12:00
"""

import requests
import json
import numpy as np
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt


def test_simple_array_endpoint():
    """Test the simplified probability array endpoint"""
    
    print("=" * 80)
    print("🧪 TESTING SIMPLE PROBABILITY ARRAY ENDPOINT")
    print("=" * 80)
    print()
    
    # Test parameters (same as Banff test)
    location = {
        "latitude": 51.1784,
        "longitude": -115.5708
    }
    
    current_time = datetime.utcnow()
    time_last_seen = current_time - timedelta(hours=4)
    
    print("📋 TEST SCENARIO")
    print("-" * 80)
    print(f"Location: Banff, Alberta")
    print(f"  Latitude:  {location['latitude']}° N")
    print(f"  Longitude: {location['longitude']}° W")
    print()
    print(f"Subject: 20-year-old male, medium experience")
    print(f"Time missing: 4 hours")
    print(f"Search radius: 5km")
    print(f"Grid resolution: 100m cells")
    print()
    
    # Create request
    request = {
        "last_known_location": location,
        "time_last_seen": time_last_seen.isoformat() + "Z",
        "subject_profile": {
            "age": 20,
            "sex": "male",
            "experience_level": "medium"
        },
        "search_radius_km": 5.0,
        "grid_resolution_m": 100.0
    }
    
    print("🚀 SENDING REQUEST TO SIMPLE ENDPOINT")
    print("-" * 80)
    print("Endpoint: POST /api/v1/predict/simple")
    print()
    print("Request:")
    print(json.dumps(request, indent=2))
    print()
    
    try:
        print("⏳ Processing (may take 8-10 seconds for API calls)...")
        print()
        
        # Make API request
        response = requests.post(
            "http://localhost:8000/api/v1/predict/simple",
            json=request,
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"❌ ERROR: Status code {response.status_code}")
            print(response.text)
            return
        
        data = response.json()
        
        # Analyze response
        print("=" * 80)
        print("✅ RESPONSE RECEIVED")
        print("=" * 80)
        print()
        
        # Extract data
        prob_grid = np.array(data['probability_grid'])
        grid_info = data['grid_info']
        
        print("📊 GRID INFORMATION")
        print("-" * 80)
        print(f"Center location: {grid_info['center_lat']:.4f}°N, {grid_info['center_lon']:.4f}°W")
        print(f"Search radius: {grid_info['radius_km']}km")
        print(f"Grid resolution: {grid_info['resolution_m']}m per cell")
        print(f"Grid size: {grid_info['grid_size']} x {grid_info['grid_size']} cells")
        print(f"Total cells: {grid_info['grid_size'] ** 2:,}")
        print(f"Hours elapsed: {grid_info['hours_elapsed']:.1f}")
        print()
        
        print("🔢 PROBABILITY ARRAY ANALYSIS")
        print("-" * 80)
        print(f"Array shape: {prob_grid.shape}")
        print(f"Array dtype: {prob_grid.dtype}")
        print()
        
        # Statistics
        non_zero = np.count_nonzero(prob_grid)
        total_prob = np.sum(prob_grid)
        max_prob = np.max(prob_grid)
        mean_prob = np.mean(prob_grid[prob_grid > 0])
        
        print(f"Total probability (should be ~1.0): {total_prob:.6f}")
        print(f"Non-zero cells: {non_zero:,} ({non_zero/prob_grid.size*100:.1f}%)")
        print(f"Zero cells: {prob_grid.size - non_zero:,}")
        print()
        print(f"Max probability: {max_prob:.6f} ({max_prob*100:.4f}%)")
        print(f"Mean probability (non-zero): {mean_prob:.6f}")
        print(f"Min probability (non-zero): {np.min(prob_grid[prob_grid > 0]):.6f}")
        print()
        
        # Find top locations
        print("🎯 TOP 10 HIGHEST PROBABILITY CELLS")
        print("-" * 80)
        
        # Get indices of top 10 probabilities
        flat_indices = np.argsort(prob_grid.ravel())[::-1][:10]
        top_indices = np.unravel_index(flat_indices, prob_grid.shape)
        
        for i, (row, col) in enumerate(zip(top_indices[0], top_indices[1]), 1):
            prob = prob_grid[row, col]
            
            # Convert to lat/lon
            lat, lon = index_to_latlon(row, col, grid_info)
            
            # Calculate distance from LKL
            distance = haversine(
                location['latitude'], location['longitude'],
                lat, lon
            )
            
            print(f"{i:2d}. Probability: {prob:.6f} ({prob*100:.4f}%)")
            print(f"    Grid position: Row {row}, Col {col}")
            print(f"    Location: {lat:.4f}°N, {lon:.4f}°W")
            print(f"    Distance from LKL: {distance:.2f}km")
            print()
        
        # Probability distribution
        print("📈 PROBABILITY DISTRIBUTION")
        print("-" * 80)
        
        high_prob = np.sum(prob_grid > 0.001)  # >0.1%
        med_prob = np.sum((prob_grid > 0.0001) & (prob_grid <= 0.001))  # 0.01-0.1%
        low_prob = np.sum((prob_grid > 0) & (prob_grid <= 0.0001))  # <0.01%
        
        print(f"High probability cells (>0.1%): {high_prob}")
        print(f"Medium probability cells (0.01-0.1%): {med_prob}")
        print(f"Low probability cells (<0.01%): {low_prob}")
        print()
        
        # Cumulative probability
        sorted_probs = np.sort(prob_grid.ravel())[::-1]
        cumsum = np.cumsum(sorted_probs)
        
        for threshold in [0.5, 0.8, 0.95]:
            cells_needed = np.searchsorted(cumsum, threshold) + 1
            print(f"{threshold*100:.0f}% of probability in top {cells_needed} cells")
        print()
        
        # Spatial analysis
        print("🗺️  SPATIAL DISTRIBUTION")
        print("-" * 80)
        
        # Find center of mass
        total_mass = prob_grid.sum()
        if total_mass > 0:
            rows, cols = np.indices(prob_grid.shape)
            center_row = np.sum(rows * prob_grid) / total_mass
            center_col = np.sum(cols * prob_grid) / total_mass
            center_lat, center_lon = index_to_latlon(int(center_row), int(center_col), grid_info)
            
            center_dist = haversine(
                location['latitude'], location['longitude'],
                center_lat, center_lon
            )
            
            print(f"Center of mass:")
            print(f"  Grid position: Row {center_row:.1f}, Col {center_col:.1f}")
            print(f"  Location: {center_lat:.4f}°N, {center_lon:.4f}°W")
            print(f"  Distance from LKL: {center_dist:.2f}km")
        print()
        
        # Generate visualization
        print("📊 GENERATING VISUALIZATION")
        print("-" * 80)
        
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
            
            # Heatmap
            im1 = ax1.imshow(prob_grid, cmap='hot', interpolation='nearest', aspect='auto')
            ax1.set_title(f'Probability Heatmap (Banff SAR - T+{grid_info["hours_elapsed"]:.1f}h)', fontsize=14)
            ax1.set_xlabel('West → East', fontsize=12)
            ax1.set_ylabel('North → South', fontsize=12)
            plt.colorbar(im1, ax=ax1, label='Probability')
            
            # Mark highest probability
            max_row, max_col = np.unravel_index(prob_grid.argmax(), prob_grid.shape)
            ax1.plot(max_col, max_row, 'b*', markersize=20, label='Highest probability')
            ax1.legend()
            
            # Log scale heatmap (better for visualization)
            log_grid = np.log10(prob_grid + 1e-10)
            im2 = ax2.imshow(log_grid, cmap='viridis', interpolation='nearest', aspect='auto')
            ax2.set_title('Log Scale Heatmap', fontsize=14)
            ax2.set_xlabel('West → East', fontsize=12)
            ax2.set_ylabel('North → South', fontsize=12)
            plt.colorbar(im2, ax=ax2, label='Log10(Probability)')
            
            plt.tight_layout()
            plt.savefig('banff_probability_heatmap.png', dpi=150, bbox_inches='tight')
            print("✓ Saved visualization to: banff_probability_heatmap.png")
            print()
        except Exception as e:
            print(f"✗ Visualization failed: {e}")
            print()
        
        # API validation
        print("=" * 80)
        print("✅ API VALIDATION")
        print("=" * 80)
        print()
        
        checks = []
        
        # Check 1: Probability sum
        prob_sum_ok = 0.99 <= total_prob <= 1.01
        checks.append(("Total probability ≈ 1.0", prob_sum_ok))
        
        # Check 2: Grid size matches
        size_ok = prob_grid.shape[0] == grid_info['grid_size']
        checks.append(("Grid size matches metadata", size_ok))
        
        # Check 3: Has non-zero probabilities
        has_probs = non_zero > 0
        checks.append(("Has non-zero probabilities", has_probs))
        
        # Check 4: Max probability is reasonable
        max_ok = 0 < max_prob < 0.1  # Should be less than 10% for spread-out distribution
        checks.append(("Max probability reasonable", max_ok))
        
        # Check 5: Array is 2D
        is_2d = len(prob_grid.shape) == 2
        checks.append(("Array is 2D", is_2d))
        
        # Check 6: Hours elapsed matches
        hours_ok = grid_info['hours_elapsed'] >= 0
        checks.append(("Hours elapsed is valid", hours_ok))
        
        for check_name, result in checks:
            status = "✓" if result else "✗"
            print(f"{status} {check_name}")
        
        all_passed = all(result for _, result in checks)
        print()
        
        if all_passed:
            print("=" * 80)
            print("✅ ALL TESTS PASSED - SIMPLE ARRAY ENDPOINT WORKING")
            print("=" * 80)
            print()
            print("APIs Used:")
            print("  ✓ Weather API (Open-Meteo) - Real conditions")
            print("  ✓ Elevation API (Open-Elevation) - Real terrain")
            print("  ✓ Behavioral Model - Age/sex specific")
            print("  ✓ Probability Engine - Time-series evolution")
            print()
            print("Output Format:")
            print("  ✓ Simple 2D probability array")
            print("  ✓ Minimal metadata")
            print("  ✓ Ready for frontend visualization")
            print()
        else:
            print("❌ SOME TESTS FAILED - Review results above")
            print()
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to API server")
        print()
        print("Please start the server first:")
        print("  cd /Users/lucas/projects/beacon-ai")
        print("  cd backend && ./start.sh")
        print()
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


def index_to_latlon(row, col, grid_info):
    """Convert grid indices to lat/lon coordinates"""
    # Calculate offsets
    lat_offset = grid_info['radius_km'] / 111.0
    lon_offset = grid_info['radius_km'] / (111.0 * np.cos(np.radians(grid_info['center_lat'])))
    
    # Grid bounds
    min_lat = grid_info['center_lat'] - lat_offset
    max_lat = grid_info['center_lat'] + lat_offset
    min_lon = grid_info['center_lon'] - lon_offset
    max_lon = grid_info['center_lon'] + lon_offset
    
    # Convert indices to coordinates
    lat = max_lat - (row / grid_info['grid_size']) * (max_lat - min_lat)
    lon = min_lon + (col / grid_info['grid_size']) * (max_lon - min_lon)
    
    return lat, lon


def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers"""
    import math
    R = 6371  # Earth radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


if __name__ == "__main__":
    test_simple_array_endpoint()
