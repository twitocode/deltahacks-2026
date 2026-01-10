const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

async function handleResponse(response: Response) {
  if (!response.ok) {
    const error = await response.text()
    throw new Error(error || response.statusText)
  }
  return response.json()
}

// Helper to generate a simple mock grid
function generateMockGrid(size: number = 50): number[][] {
  const grid: number[][] = [];
  for (let i = 0; i < size; i++) {
    const row: number[] = [];
    for (let j = 0; j < size; j++) {
      // Simple center blob
      const dist = Math.sqrt(Math.pow(i - size / 2, 2) + Math.pow(j - size / 2, 2));
      const val = Math.max(0, 1 - dist / (size / 4)); // Normalize roughly 0-1
      row.push(val);
    }
    grid.push(row);
  }
  return grid;
}

// Define the array type that the backend expects (or any structure)
export async function fetchPrediction(payload: any) {
  try {
    const response = await fetch(`${API_BASE_URL}/v1/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    })
    return await handleResponse(response)
  } catch (error) {
    console.warn("API Request failed, returning mock data:", error);
    // Return mock data compatible with the expected { [time: number]: grid[][] } structure
    // We'll return a few time steps
    return {
      0: generateMockGrid(),
      1: generateMockGrid(),
      2: generateMockGrid(),
      3: generateMockGrid(),
      6: generateMockGrid(),
      12: generateMockGrid(),
    };
  }
}
