import React, { useEffect, useRef } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";

// Interface for our SAR data properties
interface SARProperties {
  id: string;
  probability: number; // 0 to 1
  timestamp: number;
}

// Generate fake data around Hamilton, Ontario
const generateFakeSARData = (): GeoJSON.FeatureCollection => {
  const center = [-79.8711, 43.2557]; // Hamilton, ON
  const features: GeoJSON.Feature[] = [];

  for (let i = 0; i < 100; i++) {
    // Random scatter around Hamilton (~10km radius approx)
    const lng = center[0] + (Math.random() - 0.5) * 0.1;
    const lat = center[1] + (Math.random() - 0.5) * 0.1;
    
    // Weighted probability: closer to center = higher probability
    const dist = Math.sqrt(Math.pow(lng - center[0], 2) + Math.pow(lat - center[1], 2));
    const rawProb = Math.max(0, 1 - (dist / 0.05)); // Normalize roughly
    // Add some randomness to probability
    const probability = Math.min(1, Math.max(0, rawProb * (0.8 + Math.random() * 0.4)));

    features.push({
      type: "Feature",
      properties: {
        id: `pt-${i}`,
        probability: probability,
        timestamp: Date.now(),
      },
      geometry: {
        type: "Point",
        coordinates: [lng, lat],
      },
    });
  }

  return {
    type: "FeatureCollection",
    features: features,
  };
};

interface MapboxHeatmapProps {
  data?: GeoJSON.FeatureCollection;
}

export default function MapboxHeatmap({ data }: MapboxHeatmapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);

  // Use provided data or fallback to fake data
  const geoJsonData = data || generateFakeSARData();

  useEffect(() => {
    mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_API_KEY;

    if (!mapContainerRef.current) return;

    const map = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: "mapbox://styles/mapbox/dark-v11",
      center: [-79.8711, 43.2557], // Hamilton
      zoom: 12,
    });

    mapRef.current = map;

    map.on("load", () => {
      map.addSource("sar-data", {
        type: "geojson",
        data: geoJsonData as any, // Cast to avoid strict GeoJSON type mismatches with Mapbox
      });

      map.addLayer(
        {
          id: "sar-heatmap",
          type: "heatmap",
          source: "sar-data",
          maxzoom: 15,
          paint: {
            // Increase the heatmap weight based on probability
            "heatmap-weight": [
              "interpolate",
              ["linear"],
              ["get", "probability"],
              0,
              0,
              1,
              1,
            ],
            // Increase the heatmap color weight weight by zoom level
            // heatmap-intensity is a multiplier on top of heatmap-weight
            "heatmap-intensity": [
              "interpolate",
              ["linear"],
              ["zoom"],
              11,
              1,
              15,
              3,
            ],
            // Color ramp for heatmap.
            "heatmap-color": [
              "interpolate",
              ["linear"],
              ["heatmap-density"],
              0,
              "rgba(33,102,172,0)",
              0.2,
              "rgb(103,169,207)",
              0.4,
              "rgb(209,229,240)",
              0.6,
              "rgb(253,219,199)",
              0.8,
              "rgb(239,138,98)",
              1,
              "rgb(178,24,43)",
            ],
            // Adjust the heatmap radius by zoom level
            "heatmap-radius": [
              "interpolate",
              ["linear"],
              ["zoom"],
              11,
              15, // Radius at zoom 11
              15,
              30, // Radius at zoom 15
            ],
            // Transition from heatmap to circle layer by zoom level
            "heatmap-opacity": [
              "interpolate",
              ["linear"],
              ["zoom"],
              14,
              1,
              15,
              0,
            ],
          },
        },
        "waterway-label"
      );

      map.addLayer(
        {
          id: "sar-point",
          type: "circle",
          source: "sar-data",
          minzoom: 14,
          paint: {
            "circle-radius": [
              "interpolate",
              ["linear"],
              ["zoom"],
              15,
              ["interpolate", ["linear"], ["get", "probability"], 0, 5, 1, 15],
              22,
              ["interpolate", ["linear"], ["get", "probability"], 0, 10, 1, 30],
            ],
            "circle-color": [
              "interpolate",
              ["linear"],
              ["get", "probability"],
              0,
              "rgba(33,102,172,0)",
              0.2,
              "rgb(103,169,207)",
              0.4,
              "rgb(209,229,240)",
              0.6,
              "rgb(253,219,199)",
              0.8,
              "rgb(239,138,98)",
              1,
              "rgb(178,24,43)",
            ],
            "circle-stroke-color": "white",
            "circle-stroke-width": 1,
            "circle-opacity": [
              "interpolate",
              ["linear"],
              ["zoom"],
              14,
              0,
              15,
              1,
            ],
          },
        },
        "waterway-label"
      );
    });

    return () => {
      map.remove();
    };
  }, [geoJsonData]);

  return <div id="map" ref={mapContainerRef} style={{ height: "100%" }}></div>;
}