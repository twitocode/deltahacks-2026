// --- Types ---
export interface ServerGridResponse {
  metadata: {
    grid_width: number;
    grid_height: number;
    cell_size_meters: number;
    origin: {
      latitude: number;
      longitude: number;
    };
  };
  predictions: {
    [key: string]: number[][]; // "0": [[...]], "1": [[...]]
  };
}

// --- Gaussian Generator (Returns RAW MATRIX, not GeoJSON) ---
export const generateFakeServerResponse = (center: [number, number]): ServerGridResponse => {
  const gridSize = 50;
  const cellSizeMeters = 500;
  
  // Define "Hotspots" (Gaussian Centers) relative to index (0-50)
  // Center of grid is 25,25
  const hotspots = [
    { x: 25, y: 25, intensity: 1.0, spread: 4.0 }, // Main (Center)
    { x: 35, y: 30, intensity: 0.7, spread: 6.0 }, // Secondary
    { x: 15, y: 10, intensity: 0.5, spread: 8.0 }, // Wide wander
    { x: 40, y: 15, intensity: 0.6, spread: 3.0 }  // Small cluster
  ];

  const gaussian = (x: number, y: number, cx: number, cy: number, spread: number) => {
    const d2 = Math.pow(x - cx, 2) + Math.pow(y - cy, 2);
    return Math.exp(-d2 / (2 * spread * spread));
  };

  const grid: number[][] = [];

  for (let j = 0; j < gridSize; j++) { // Rows (Latitude)
    const row: number[] = [];
    for (let i = 0; i < gridSize; i++) { // Cols (Longitude)
      let probability = 0;
      for (const h of hotspots) {
        probability += h.intensity * gaussian(i, j, h.x, h.y, h.spread);
      }
      // Clamp and threshold
      probability = Math.min(1, Math.max(0, probability));
      row.push(probability);
    }
    grid.push(row);
  }

  // Create mock response with this single grid for hour "0"
  // For a real app, you'd vary the 'hotspots' for hours 1, 2, 3...
  return {
    metadata: {
      grid_width: gridSize,
      grid_height: gridSize,
      cell_size_meters: cellSizeMeters,
      origin: {
        latitude: center[1],
        longitude: center[0]
      }
    },
    predictions: {
      "0": grid,
      "1": grid.map(r => r.map(v => v * 0.9)), // Fake decay for hour 1
      "3": grid.map(r => r.map(v => v * 0.7)), // Fake decay for hour 3
      "6": grid.map(r => r.map(v => v * 0.5)),
      "12": grid.map(r => r.map(v => v * 0.3)),
    }
  };
};

// --- Adapter: Converts Server Response -> Mapbox GeoJSON ---
export const convertServerGridToGeoJSON = (
  response: ServerGridResponse, 
  hourKey: string = "0"
): GeoJSON.FeatureCollection => {
  const features: GeoJSON.Feature[] = [];
  const { origin, grid_width, grid_height, cell_size_meters } = response.metadata;
  
  // Approx conversion: 1 degree lat ~ 111,000 meters
  // 1 degree lng ~ 111,000 * cos(lat) meters
  const metersPerDegLat = 111000;
  const metersPerDegLng = 111000 * Math.cos(origin.latitude * (Math.PI / 180));
  
  const latStep = cell_size_meters / metersPerDegLat;
  const lngStep = cell_size_meters / metersPerDegLng;

  // Calculate Grid Bounds (centered on origin)
  const startLng = origin.longitude - (grid_width * lngStep) / 2;
  const startLat = origin.latitude - (grid_height * latStep) / 2;

  const gridData = response.predictions[hourKey] || response.predictions["0"];

  if (!gridData) return { type: "FeatureCollection", features: [] };

  // Loop Rows (Lat) and Cols (Lng)
  // Note: response.predictions[row][col]. Row 0 is typically Top (North) or Bottom (South).
  // In our generator, Row 0 is bottom (y=0). Let's assume Row 0 = Min Lat.
  for (let j = 0; j < grid_height; j++) {
    for (let i = 0; i < grid_width; i++) {
      const probability = gridData[j][i];

      // Threshold to reduce Mapbox load
      if (probability < 0.02) continue;

      const minLng = startLng + i * lngStep;
      const minLat = startLat + j * latStep;
      const maxLng = minLng + lngStep;
      const maxLat = minLat + latStep;

      features.push({
        type: "Feature",
        properties: {
          id: `cell-${i}-${j}`,
          probability: probability,
        },
        geometry: {
          type: "Polygon",
          coordinates: [[
            [minLng, minLat],
            [maxLng, minLat],
            [maxLng, maxLat],
            [minLng, maxLat],
            [minLng, minLat] // Close loop
          ]],
        },
      });
    }
  }

  return {
    type: "FeatureCollection",
    features: features,
  };
};
