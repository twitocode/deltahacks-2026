# Search and Rescue Heatmap API Specification

This document defines the required JSON response format for the `/v1/search` endpoint. This format is critical for the frontend to correctly render the 3D probability grid heatmap using Mapbox.

## Overview

*   **Endpoint:** `POST /v1/search`
*   **Goal:** Return a probability distribution grid for different time intervals.
*   **Grid Dimensions:** 50x50 cells (2,500 total data points per time step).
*   **Data Type:** 2D Array (Matrix) of floating-point numbers (`0.0` to `1.0`).

## Request Payload

```json
{
  "latitude": 48.3562,
  "longitude": -120.6848,
  "age": 35,
  "sex": "male",
  "experience": "novice",
  "time_last_seen": "2023-10-27T10:00:00Z"
}
```

## Response Payload

The response MUST follow this structure exactly to map correctly to the frontend's grid generator.

### Structure

```json
{
  "metadata": {
    "grid_width": 50,
    "grid_height": 50,
    "cell_size_meters": 500,
    "origin": {
      "latitude": 48.3562,
      "longitude": -120.6848
    }
  },
  "predictions": {
    "0": [ [number, number, ...], ... ], // 50x50 Matrix for Hour 0
    "1": [ [number, number, ...], ... ], // 50x50 Matrix for Hour 1
    "3": [ [number, number, ...], ... ], // 50x50 Matrix for Hour 3
    "6": [ [number, number, ...], ... ], // 50x50 Matrix for Hour 6
    "12": [ [number, number, ...], ... ] // 50x50 Matrix for Hour 12
  }
}
```

### Field Definitions

| Field | Type | Description |
| :--- | :--- | :--- |
| `metadata.grid_width` | `integer` | **Must be 50**. Number of columns (Longitude steps). |
| `metadata.grid_height` | `integer` | **Must be 50**. Number of rows (Latitude steps). |
| `metadata.cell_size_meters` | `number` | Physical size of one grid square (e.g., `500` meters). Used to calculate corner coordinates. |
| `metadata.origin` | `object` | The center point (or top-left) of the search area. Matches request coordinates. |
| `predictions` | `object` | Key-value map where keys are **Hours Elapsed** (string) and values are the **Probability Matrices**. |
| `predictions["X"]` | `number[][]` | A 2D Array of probabilities. |

### The Probability Matrix (`number[][]`)

*   **Outer Array:** Represents **Rows** (Latitude / North-to-South). Index `0` is the Top (North) row.
*   **Inner Array:** Represents **Columns** (Longitude / West-to-East). Index `0` is the Left (West) column.
*   **Values:** Floats between `0.0` (0% probability) and `1.0` (100% probability).

**Visual Layout:**

```
Row 0:  [ (North-West), ..., (North-East) ]
Row 1:  [ ... ]
...
Row 49: [ (South-West), ..., (South-East) ]
```

## Example JSON Response

```json
{
  "metadata": {
    "grid_width": 50,
    "grid_height": 50,
    "cell_size_meters": 500,
    "origin": {
      "latitude": 48.3562,
      "longitude": -120.6848
    }
  },
  "predictions": {
    "0": [
      [0.0, 0.0, 0.0, 0.05, 0.12, ... (45 more numbers) ... ],
      [0.0, 0.01, 0.02, 0.25, 0.85, ... (45 more numbers) ... ],
      ... (48 more rows) ...
    ],
    "1": [
      [0.0, 0.0, 0.02, 0.08, 0.15, ... ],
      ...
    ]
  }
}
```
