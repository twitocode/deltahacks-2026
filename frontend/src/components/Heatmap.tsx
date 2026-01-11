import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import { useEffect, useRef, useState } from "react";

interface MapboxHeatmapProps {
  data?: GeoJSON.FeatureCollection;
  onMapClick?: (lat: number, lng: number) => void;
  center?: [number, number];
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
    // @ts-ignore
    mapboxgl.config.DISABLE_TELEMETRY = true;
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
      console.log("[MapboxHeatmap] Map loaded successfully.");
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
          // Interpolate color based on probability - Green/Yellow/Orange/Red scheme
          "fill-color": [
            "interpolate",
            ["linear"],
            ["get", "probability"],
            0.01,
            "rgba(34,139,34,0)", // Transparent threshold (forest green)
            0.1,
            "rgb(144,238,144)", // Light Green (Low)
            0.25,
            "rgb(173,255,47)", // Green-Yellow
            0.4,
            "rgb(255,255,0)", // Yellow
            0.55,
            "rgb(255,215,0)", // Gold
            0.7,
            "rgb(255,165,0)", // Orange
            0.85,
            "rgb(255,69,0)", // Orange-Red
            1.0,
            "rgb(220,20,60)", // Crimson (High)
          ],
          "fill-opacity": 0.65, // Semi-transparent so terrain is visible
          "fill-outline-color": "rgba(255,255,255,0.08)", // Very faint grid lines
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
      console.log(
        `[MapboxHeatmap] Map clicked at Lat: ${lat.toFixed(
          6
        )}, Lng: ${lng.toFixed(6)}`
      );
      setSelectedPoint([lng, lat]);
      if (onMapClick) onMapClick(lat, lng);
    });

    return () => {
      console.log("[MapboxHeatmap] Removing map instance.");
      map.remove();
    };
  }, []);

  // Reactive Data Update (Grid)
  useEffect(() => {
    if (!mapRef.current || !mapRef.current.isStyleLoaded()) return;
    const source = mapRef.current.getSource(
      "sar-grid"
    ) as mapboxgl.GeoJSONSource;
    if (source && data) {
      console.log(
        "[MapboxHeatmap] Updating grid data source. Feature count:",
        data.features.length
      );
      source.setData(data);
    }
  }, [data]);

  // Reactive Selection Update
  useEffect(() => {
    if (!mapRef.current || !mapRef.current.isStyleLoaded()) return;
    const source = mapRef.current.getSource(
      "selection-point"
    ) as mapboxgl.GeoJSONSource;
    if (source) {
      if (selectedPoint) {
        // console.log("[MapboxHeatmap] Updating selection point:", selectedPoint);
        source.setData({
          type: "FeatureCollection",
          features: [
            {
              type: "Feature",
              properties: {},
              geometry: { type: "Point", coordinates: selectedPoint },
            },
          ],
        });
      } else {
        source.setData({ type: "FeatureCollection", features: [] });
      }
    }
  }, [selectedPoint]);

  // Reactive Center Update
  useEffect(() => {
    if (!mapRef.current || !center) return;
    console.log("[MapboxHeatmap] Flying to new center:", center);
    mapRef.current.flyTo({
      center: center,
      zoom: 12,
      pitch: 60, // Maintain 3D pitch
      essential: true,
    });
  }, [center]);

  return <div id="map" ref={mapContainerRef} style={{ height: "100%" }}></div>;
}
