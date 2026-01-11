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

// --- Cellular Path Generator (BFS with Noise) ---
// Creates hotspots that "grow" branching paths outward
export const generateFakeServerResponse = (
  center: [number, number]
): ServerGridResponse => {
  console.log(
    `[HeatmapGen] Generating fake server response for center: ${center}`
  );
  const genStart = performance.now();
  const gridSize = 50; // 50x50 grid matching backend
  const cellSizeMeters = 500; // 500m cells matching backend cell_size_meters

  // Initialize grid
  const grid: number[][] = Array(gridSize)
    .fill(0)
    .map(() => Array(gridSize).fill(0));

  // Noise map for "Terrain Resistance"
  // Simple random noise is enough to make paths branch
  const resistance: number[][] = Array(gridSize)
    .fill(0)
    .map(() =>
      Array(gridSize)
        .fill(0)
        .map(() => Math.random())
    );

  // Queue for BFS: [x, y, value]
  const queue: [number, number, number][] = [];

  // 1. Plant Seeds (Hotspots)
  const seeds = 8; // Number of distinct hotspots
  console.log(`[HeatmapGen] Planting ${seeds} seeds...`);

  for (let k = 0; k < seeds; k++) {
    // Scatter seeds around the center, but not too far
    const center = Math.floor(gridSize / 2);
    const spread = Math.floor(gridSize / 3);
    const sx = Math.floor(center + (Math.random() - 0.5) * spread);
    const sy = Math.floor(center + (Math.random() - 0.5) * spread);

    if (sx >= 0 && sx < gridSize && sy >= 0 && sy < gridSize) {
      grid[sy][sx] = 1.0;
      queue.push([sx, sy, 1.0]);
    }
  }

  // 2. Spread (BFS)
  // Directions: Up, Down, Left, Right
  const dirs = [
    [0, 1],
    [0, -1],
    [1, 0],
    [-1, 0],
  ];
  let iterations = 0;

  while (queue.length > 0) {
    iterations++;
    // Pop random element to make growth more organic (instead of standard FIFO)
    const idx = Math.floor(Math.random() * queue.length);
    const [cx, cy, val] = queue.splice(idx, 1)[0];

    // Stop if value is too low
    if (val < 0.05) continue;

    for (const [dx, dy] of dirs) {
      const nx = cx + dx;
      const ny = cy + dy;

      if (nx >= 0 && nx < gridSize && ny >= 0 && ny < gridSize) {
        // Calculate new value: Decay based on resistance
        // High resistance = High decay = Path blocked
        // Low resistance = Low decay = Path continues
        const decay = 0.005 + resistance[ny][nx] * 0.04;
        const newVal = val - decay;

        // If new value is better than what's there, update and push to queue
        if (newVal > grid[ny][nx]) {
          grid[ny][nx] = newVal;
          queue.push([nx, ny, newVal]);
        }
      }
    }
  }

  const genEnd = performance.now();
  console.log(
    `[HeatmapGen] Generation complete. Iterations: ${iterations}, Time: ${(
      genEnd - genStart
    ).toFixed(2)}ms`
  );

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
      "1": grid.map((r) => r.map((v) => v * 0.95)), // Fade over time
      "3": grid.map((r) => r.map((v) => v * 0.8)),
      "6": grid.map((r) => r.map((v) => v * 0.6)),
      "12": grid.map((r) => r.map((v) => v * 0.4)),
    },
  };
};

// --- Adapter: Interpolates & Converts Server Response -> Mapbox GeoJSON ---
export const convertServerGridToGeoJSON = (
  response: ServerGridResponse,
  timeValue: number = 0
): GeoJSON.FeatureCollection => {
  const convStart = performance.now();
  const features: GeoJSON.Feature[] = [];
  const { origin, grid_width, grid_height, cell_size_meters } =
    response.metadata;

  // Debug: Log actual values being used
  const totalWidthKm = (grid_width * cell_size_meters) / 1000;
  const totalHeightKm = (grid_height * cell_size_meters) / 1000;
  console.log(`[HeatmapGen] Grid metadata:`, {
    origin,
    grid_width,
    grid_height,
    cell_size_meters,
    totalWidthKm,
    totalHeightKm,
  });

  // Approx conversion
  const metersPerDegLat = 111000;
  const metersPerDegLng = 111000 * Math.cos(origin.latitude * (Math.PI / 180));

  const latStep = cell_size_meters / metersPerDegLat;
  const lngStep = cell_size_meters / metersPerDegLng;

  // Calculate Grid Bounds (centered on origin)
  const startLng = origin.longitude - (grid_width * lngStep) / 2;
  const startLat = origin.latitude - (grid_height * latStep) / 2;

  const hourKey = String(timeValue);

  // Find the closest available time key
  let bestKey = "0";
  const availableKeys = Object.keys(response.predictions);
  if (availableKeys.length > 0) {
    let minDiff = Infinity;
    for (const key of availableKeys) {
      const diff = Math.abs(parseFloat(key) - timeValue);
      if (diff < minDiff) {
        minDiff = diff;
        bestKey = key;
      }
    }
  }

  const gridData =
    response.predictions[hourKey] || response.predictions[bestKey];

  console.log(
    `[HeatmapGen] Converting grid to GeoJSON for time: ${timeValue} (best match: ${bestKey})`
  );

  if (!gridData) {
    console.warn(`[HeatmapGen] No grid data found for time ${timeValue}`);
    return { type: "FeatureCollection", features: [] };
  }

  for (let j = 0; j < grid_height; j++) {
    for (let i = 0; i < grid_width; i++) {
      const probability = gridData[j][i];

      // Threshold: Only visualize areas with some probability
      if (probability < 0.01) continue;

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

  const convEnd = performance.now();
  console.log(
    `[HeatmapGen] Conversion complete. Features: ${features.length}, Time: ${(
      convEnd - convStart
    ).toFixed(2)}ms`
  );

  return {
    type: "FeatureCollection",
    features: features,
  };
};
