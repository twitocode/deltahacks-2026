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
  try {
    const response = await fetch(`${API_BASE_URL}/v1/search`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    return await handleResponse(response);
  } catch (error) {
    console.warn("API Request failed, returning mock Gaussian grid:", error);

    // FALLBACK: Generate fake data at the requested location
    // The delay simulates a network request for better UX feel
    await new Promise((resolve) => setTimeout(resolve, 800));

    return generateFakeServerResponse([payload.longitude, payload.latitude]);
  }
}
