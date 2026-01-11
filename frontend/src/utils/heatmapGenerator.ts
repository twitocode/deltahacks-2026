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

// --- Path-Based Gaussian Generator ---
// Simulates "Random Walkers" to create probability paths
export const generateFakeServerResponse = (center: [number, number]): ServerGridResponse => {
  const gridSize = 300; // 90,000 cells
  const cellSizeMeters = 20; // Very fine grain (~20m)
  
  // Initialize grid with zeros
  const grid: number[][] = Array(gridSize).fill(0).map(() => Array(gridSize).fill(0));

  // Helper: Add Gaussian "Splat" at x,y
  const addSplat = (gx: number, gy: number, intensity: number, spread: number) => {
    const radius = Math.ceil(spread * 3);
    const minX = Math.max(0, Math.floor(gx - radius));
    const maxX = Math.min(gridSize - 1, Math.ceil(gx + radius));
    const minY = Math.max(0, Math.floor(gy - radius));
    const maxY = Math.min(gridSize - 1, Math.ceil(gy + radius));

    for (let y = minY; y <= maxY; y++) {
      for (let x = minX; x <= maxX; x++) {
        const d2 = Math.pow(x - gx, 2) + Math.pow(y - gy, 2);
        const val = intensity * Math.exp(-d2 / (2 * spread * spread));
        grid[y][x] += val;
      }
    }
  };

  // 1. Simulate Paths (Random Walkers)
  const startX = 150; // Center of 300x300
  const startY = 150;

  // Define 4 "Walker" scenarios with MASSIVE steps to cover km distances
  // At 20m/cell, 500 steps = 10km.
  const walkers = [
    { dirX: 0.6, dirY: 0.4, steps: 600, spread: 8.0, weight: 0.6 }, 
    { dirX: -0.4, dirY: 0.6, steps: 500, spread: 10.0, weight: 0.4 }, 
    { dirX: 0.2, dirY: -0.8, steps: 400, spread: 12.0, weight: 0.3 },
    { dirX: -0.7, dirY: -0.3, steps: 450, spread: 9.0, weight: 0.5 },
  ];

  walkers.forEach((walker) => {
    let cx = startX;
    let cy = startY;

    // Add strong initial point (LKP)
    addSplat(cx, cy, 0.8, 2.0);

    for (let s = 0; s < walker.steps; s++) {
      // Move in general direction + some randomness (Perlin-ish wiggle)
      cx += walker.dirX + (Math.random() - 0.5) * 1.5;
      cy += walker.dirY + (Math.random() - 0.5) * 1.5;

      // Add probability blob at new step
      // Intensity fades as they get further away
      const fade = 1 - s / walker.steps;
      addSplat(cx, cy, walker.weight * fade, walker.spread);
    }
  });

  // 2. Normalize Grid (0 to 1)
  let maxVal = 0;
  for (const row of grid) for (const v of row) if (v > maxVal) maxVal = v;
  if (maxVal > 0) {
    for (let y = 0; y < gridSize; y++) {
      for (let x = 0; x < gridSize; x++) {
        grid[y][x] /= maxVal;
      }
    }
  }

  // Create mock response
  return {
    metadata: {
      grid_width: gridSize,
      grid_height: gridSize,
      cell_size_meters: cellSizeMeters,
      origin: {
        latitude: center[1],
        longitude: center[0],
      },
    },
    predictions: {
      "0": grid,
      // Create simplistic time-steps by blurring/spreading the grid
      "1": grid.map((r) => r.map((v) => v * 0.95)),
      "3": grid.map((r) => r.map((v) => v * 0.8)),
      "6": grid.map((r) => r.map((v) => v * 0.6)),
      "12": grid.map((r) => r.map((v) => v * 0.4)),
    },
  };
};

// --- Adapter: Converts Server Response -> Mapbox GeoJSON ---
export const convertServerGridToGeoJSON = (
  response: ServerGridResponse,
  hourKey: string = "0"
): GeoJSON.FeatureCollection => {
  const features: GeoJSON.Feature[] = [];
  const { origin, grid_width, grid_height, cell_size_meters } =
    response.metadata;

  // Approx conversion
  const metersPerDegLat = 111000;
  const metersPerDegLng = 111000 * Math.cos(origin.latitude * (Math.PI / 180));

  const latStep = cell_size_meters / metersPerDegLat;
  const lngStep = cell_size_meters / metersPerDegLng;

  // Calculate Grid Bounds (centered on origin)
  const startLng = origin.longitude - (grid_width * lngStep) / 2;
  const startLat = origin.latitude - (grid_height * latStep) / 2;

  const gridData = response.predictions[hourKey] || response.predictions["0"];

  if (!gridData) return { type: "FeatureCollection", features: [] };

  for (let j = 0; j < grid_height; j++) {
    for (let i = 0; i < grid_width; i++) {
      const probability = gridData[j][i];

      // Threshold: Only visualize areas with some probability
      if (probability < 0.05) continue;

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
          coordinates: [
            [
              [minLng, minLat],
              [maxLng, minLat],
              [maxLng, maxLat],
              [minLng, maxLat],
              [minLng, minLat], // Close loop
            ],
          ],
        },
      });
    }
  }

  return {
    type: "FeatureCollection",
    features: features,
  };
};
