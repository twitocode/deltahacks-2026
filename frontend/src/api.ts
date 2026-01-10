const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api'

async function handleResponse(response: Response) {
  if (!response.ok) {
    const error = await response.text()
    throw new Error(error || response.statusText)
  }
  return response.json()
}

export async function fetchItems() {
  const response = await fetch(`${API_BASE_URL}/items`)
  return handleResponse(response)
}
