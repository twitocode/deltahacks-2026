import {
  generateFakeServerResponse,
  type ServerGridResponse,
} from "./utils/heatmapGenerator";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

async function handleResponse(response: Response): Promise<ServerGridResponse> {
  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || response.statusText);
  }
  return response.json();
}

// Fetch prediction from server, or fallback to fake generator on error
export async function fetchPrediction(payload: {
  latitude: number;
  longitude: number;
  [key: string]: any;
}): Promise<ServerGridResponse> {
  console.log("[API] fetchPrediction called with payload:", payload);
  const startTime = performance.now();

  try {
    const url = `${API_BASE_URL}/v1/search`;
    console.log(`[API] sending POST request to ${url}`);
    
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    
    const data = await handleResponse(response);
    const endTime = performance.now();
    console.log(`[API] fetchPrediction success in ${(endTime - startTime).toFixed(2)}ms`);
    return data;
  } catch (error) {
    const endTime = performance.now();
    console.warn(`[API] fetchPrediction failed after ${(endTime - startTime).toFixed(2)}ms. Error:`, error);
    console.log("[API] Falling back to mock data generator...");

    // FALLBACK: Generate fake data at the requested location
    // The delay simulates a network request for better UX feel
    await new Promise((resolve) => setTimeout(resolve, 800));

    const mockData = generateFakeServerResponse([payload.longitude, payload.latitude]);
    console.log("[API] Mock data generated successfully.");
    return mockData;
  }
}
