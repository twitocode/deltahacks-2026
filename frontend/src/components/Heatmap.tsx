import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import { useEffect, useRef, useState } from "react";

interface MapboxHeatmapProps {
  data?: GeoJSON.FeatureCollection;
  onMapClick?: (lat: number, lng: number) => void;
  center?: [number, number]; // Optional center to fly to
}

export default function MapboxHeatmap({
  data,
  onMapClick,
  center,
}: MapboxHeatmapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const [selectedPoint, setSelectedPoint] = useState<[number, number] | null>(
    null
  );

  useEffect(() => {
    mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_API_KEY;

    if (!mapContainerRef.current) return;

    // Default center if none provided (e.g. initial load)
    const initialCenter = center || [-120.6848, 48.3562];

    const map = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: "mapbox://styles/mapbox/standard",
      center: initialCenter,
      zoom: 12,
      pitch: 45,
      bearing: 0,
    });

    mapRef.current = map;

    map.on("load", () => {
      // Add empty source initially if no data
      map.addSource("sar-grid", {
        type: "geojson",
        data: data || { type: "FeatureCollection", features: [] },
      });

      // FILL LAYER for Grid Heatmap
      map.addLayer({
        id: "sar-grid-fill",
        type: "fill",
        source: "sar-grid",
        slot: "top",
        paint: {
          "fill-color": [
            "interpolate",
            ["linear"],
            ["get", "probability"],
            0.15,
            "rgba(33,102,172,0)", // Transparent at low prob
            0.3,
            "rgb(103,169,207)", // Blue
            0.5,
            "rgb(209,229,240)", // Light Blue
            0.7,
            "rgb(253,219,199)", // Light Orange
            0.85,
            "rgb(239,138,98)", // Orange
            1.0,
            "rgb(178,24,43)", // Red
          ],
          "fill-opacity": 0.7,
          "fill-outline-color": "rgba(255,255,255,0.1)",
        },
      });

      // Add source and layer for selection marker
      map.addSource("selection-point", {
        type: "geojson",
        data: {
          type: "FeatureCollection",
          features: [],
        },
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
      if (onMapClick) {
        onMapClick(lat, lng);
      }
    });

    return () => {
      map.remove();
    };
  }, []); // Run once on mount

  // Update Grid Data Source when `data` prop changes
  useEffect(() => {
    if (!mapRef.current || !mapRef.current.isStyleLoaded()) return;

    const source = mapRef.current.getSource(
      "sar-grid"
    ) as mapboxgl.GeoJSONSource;
    if (source && data) {
      source.setData(data);
    }
  }, [data]);

  // Update Selection Point Source
  useEffect(() => {
    if (!mapRef.current || !mapRef.current.isStyleLoaded()) return;

    const source = mapRef.current.getSource(
      "selection-point"
    ) as mapboxgl.GeoJSONSource;
    if (source) {
      if (selectedPoint) {
        source.setData({
          type: "FeatureCollection",
          features: [
            {
              type: "Feature",
              properties: {},
              geometry: {
                type: "Point",
                coordinates: selectedPoint,
              },
            },
          ],
        });
      } else {
        source.setData({
          type: "FeatureCollection",
          features: [],
        });
      }
    }
  }, [selectedPoint]);

  // Fly to new center when `center` prop changes
  useEffect(() => {
    if (!mapRef.current || !center) return;
    mapRef.current.flyTo({
      center: center,
      zoom: 12,
      essential: true,
    });
  }, [center]);

  return <div id="map" ref={mapContainerRef} style={{ height: "100%" }}></div>;
}
