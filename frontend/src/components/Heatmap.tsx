import React, { useEffect, useRef, useState } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";

interface MapboxHeatmapProps {
  data?: GeoJSON.FeatureCollection;
  onMapClick?: (lat: number, lng: number) => void;
  center?: [number, number];
}

export default function MapboxHeatmap({ data, onMapClick, center }: MapboxHeatmapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const [selectedPoint, setSelectedPoint] = useState<[number, number] | null>(null);

  useEffect(() => {
    mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_API_KEY;

    if (!mapContainerRef.current) return;

    const initialCenter = center || [-120.6848, 48.3562];

    const map = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: "mapbox://styles/mapbox/standard",
      center: initialCenter,
      zoom: 12,
      pitch: 60, // Start steeper
      minPitch: 60, // Force 3D view always
      maxPitch: 85,
      bearing: 0,
    });

    mapRef.current = map;

    map.on("load", () => {
      // Add Grid Source
      map.addSource("sar-grid", {
        type: "geojson",
        data: data || { type: "FeatureCollection", features: [] },
      });

      // --- CHOROPLETH (Grid) LAYER ---
      map.addLayer({
        id: "sar-grid-fill",
        type: "fill",
        source: "sar-grid",
        slot: "top", // Drapes over terrain in Standard style
        paint: {
          // Interpolate color based on probability
          "fill-color": [
            "interpolate",
            ["linear"],
            ["get", "probability"],
            0.05, "rgba(33,102,172,0)",   // Transparent threshold
            0.2, "rgb(103,169,207)",      // Blue (Low)
            0.4, "rgb(209,229,240)",      // Light Blue
            0.6, "rgb(253,219,199)",      // Peach
            0.8, "rgb(239,138,98)",       // Orange
            1.0, "rgb(178,24,43)"         // Red (High)
          ],
          "fill-opacity": 0.6, // Semi-transparent so terrain is visible
          "fill-outline-color": "rgba(255,255,255,0.05)" // Very faint grid lines
        },
      });

      // --- SELECTION MARKER ---
      map.addSource("selection-point", {
        type: "geojson",
        data: { type: "FeatureCollection", features: [] },
      });

      map.addLayer({
        id: "selection-point-layer",
        type: "circle",
        source: "selection-point",
        slot: "top",
        paint: {
          "circle-radius": 8,
          "circle-color": "#ffffff",
          "circle-stroke-width": 2,
          "circle-stroke-color": "#000000",
          "circle-emissive-strength": 1,
        },
      });
    });

    map.on("click", (e) => {
      const { lng, lat } = e.lngLat;
      setSelectedPoint([lng, lat]);
      if (onMapClick) onMapClick(lat, lng);
    });

    return () => {
      map.remove();
    };
  }, []);

  // Reactive Data Update (Grid)
  useEffect(() => {
    if (!mapRef.current || !mapRef.current.isStyleLoaded()) return;
    const source = mapRef.current.getSource("sar-grid") as mapboxgl.GeoJSONSource;
    if (source && data) {
      source.setData(data);
    }
  }, [data]);

  // Reactive Selection Update
  useEffect(() => {
    if (!mapRef.current || !mapRef.current.isStyleLoaded()) return;
    const source = mapRef.current.getSource("selection-point") as mapboxgl.GeoJSONSource;
    if (source) {
      if (selectedPoint) {
        source.setData({
          type: "FeatureCollection",
          features: [{
            type: "Feature",
            properties: {},
            geometry: { type: "Point", coordinates: selectedPoint },
          }],
        });
      } else {
        source.setData({ type: "FeatureCollection", features: [] });
      }
    }
  }, [selectedPoint]);

  // Reactive Center Update
  useEffect(() => {
    if (!mapRef.current || !center) return;
    mapRef.current.flyTo({ 
      center: center, 
      zoom: 12, 
      pitch: 60, // Maintain 3D pitch
      essential: true 
    });
  }, [center]);

  return <div id="map" ref={mapContainerRef} style={{ height: "100%" }}></div>;
}
