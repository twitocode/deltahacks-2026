#!/usr/bin/env python3
"""
Probability Distribution Analyzer for WayPoint Search API

Fetches predictions from the /api/v1/search endpoint and analyzes
the distribution of probability values across the grid.
"""

import requests
import numpy as np
from datetime import datetime
from collections import Counter

API_URL = "http://localhost:8000/api/v1/search"

def fetch_predictions(lat: float = 48.3562, lon: float = -120.6848):
    """Fetch predictions from the search API."""
    payload = {
        "latitude": lat,
        "longitude": lon,
        "time_last_seen": datetime.now().isoformat(),
        "experience": "intermediate",
        "age": 35
    }
    
    print(f"Fetching predictions for ({lat}, {lon})...")
    response = requests.post(API_URL, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()

def analyze_distribution(data: dict):
    """Analyze probability distribution across all time slices."""
    metadata = data["metadata"]
    predictions = data["predictions"]
    
    print("\n" + "="*60)
    print("GRID METADATA")
    print("="*60)
    print(f"Grid Size: {metadata['grid_width']} x {metadata['grid_height']}")
    print(f"Cell Size: {metadata['cell_size_meters']}m")
    print(f"Origin: ({metadata['origin']['latitude']:.4f}, {metadata['origin']['longitude']:.4f})")
    total_cells = metadata['grid_width'] * metadata['grid_height']
    print(f"Total Cells: {total_cells}")
    
    for hour_key, grid in sorted(predictions.items(), key=lambda x: float(x[0])):
        hour = float(hour_key)
        flat = np.array(grid).flatten()
        
        print("\n" + "="*60)
        print(f"HOUR {hour}h")
        print("="*60)
        
        # Basic stats
        non_zero = flat[flat > 0]
        print(f"\n📊 BASIC STATISTICS:")
        print(f"   Min:    {flat.min():.6f}")
        print(f"   Max:    {flat.max():.6f}")
        print(f"   Mean:   {flat.mean():.6f}")
        print(f"   Median: {np.median(flat):.6f}")
        print(f"   Std:    {flat.std():.6f}")
        
        # Distribution buckets
        buckets = [0, 0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9, 1.0]
        print(f"\n📈 PROBABILITY DISTRIBUTION:")
        
        for i in range(len(buckets) - 1):
            low, high = buckets[i], buckets[i+1]
            count = np.sum((flat >= low) & (flat < high))
            pct = (count / total_cells) * 100
            bar = "█" * int(pct / 2)
            print(f"   [{low:.2f}-{high:.2f}): {count:5d} ({pct:5.1f}%) {bar}")
        
        # Cells >= 1.0
        count_max = np.sum(flat >= 1.0)
        print(f"   [1.00]:      {count_max:5d} ({count_max/total_cells*100:5.1f}%)")
        
        # Summary
        cells_above_01 = np.sum(flat > 0.01)
        cells_above_05 = np.sum(flat > 0.05)
        cells_above_10 = np.sum(flat > 0.1)
        cells_above_50 = np.sum(flat > 0.5)
        
        print(f"\n📍 CELLS ABOVE THRESHOLD:")
        print(f"   > 0.01: {cells_above_01:4d} cells ({cells_above_01/total_cells*100:.1f}%)")
        print(f"   > 0.05: {cells_above_05:4d} cells ({cells_above_05/total_cells*100:.1f}%)")
        print(f"   > 0.10: {cells_above_10:4d} cells ({cells_above_10/total_cells*100:.1f}%)")
        print(f"   > 0.50: {cells_above_50:4d} cells ({cells_above_50/total_cells*100:.1f}%)")
        
        # Top 10 highest probability cells
        top_indices = np.argsort(flat)[-10:][::-1]
        print(f"\n🔥 TOP 10 HIGHEST PROBABILITY CELLS:")
        for idx in top_indices:
            row = idx // metadata['grid_width']
            col = idx % metadata['grid_width']
            prob = flat[idx]
            print(f"   Cell [{row:2d},{col:2d}]: {prob:.4f}")

def main():
    try:
        data = fetch_predictions()
        analyze_distribution(data)
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API at", API_URL)
        print("   Make sure the backend server is running (uvicorn app.main:app)")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
