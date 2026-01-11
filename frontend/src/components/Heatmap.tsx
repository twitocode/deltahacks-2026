import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import { useEffect, useRef } from "react";

interface MapboxHeatmapProps {
  data?: GeoJSON.FeatureCollection;
  onMapClick?: (lat: number, lng: number) => void;
  center?: [number, number];
  selectedPoint?: [number, number] | null;
  is3D?: boolean;
  isDarkMode?: boolean;
}

// Style URLs
const STYLE_3D = "mapbox://styles/mapbox/standard";
const STYLE_2D_DARK = "mapbox://styles/mapbox/navigation-night-v1";
const STYLE_2D_LIGHT = "mapbox://styles/mapbox/streets-v12";

export default function MapboxHeatmap({
  data,
  onMapClick,
  center,
  selectedPoint,
  is3D = true,
  isDarkMode = true,
}: MapboxHeatmapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const popupRef = useRef<mapboxgl.Popup | null>(null);
  const dataRef = useRef<GeoJSON.FeatureCollection | undefined>(data);
  const selectedPointRef = useRef<[number, number] | null | undefined>(
    selectedPoint
  );
  // Spin state
  const isSpinningRef = useRef(!center && !selectedPoint);

  // Keep refs in sync
  useEffect(() => {
    dataRef.current = data;
  }, [data]);

  useEffect(() => {
    selectedPointRef.current = selectedPoint;
  }, [selectedPoint]);

  // Helper to add our custom layers to the map
  const addCustomLayers = (map: mapboxgl.Map) => {
    // Add Grid Source
    if (!map.getSource("sar-grid")) {
      map.addSource("sar-grid", {
        type: "geojson",
        data: dataRef.current || { type: "FeatureCollection", features: [] },
      });
    }

    // --- CHOROPLETH (Grid) LAYER ---
    if (!map.getLayer("sar-grid-fill")) {
      map.addLayer({
        id: "sar-grid-fill",
        type: "fill",
        source: "sar-grid",
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
          "fill-emissive-strength": 1, // Makes colors vibrant in 3D night mode
        },
      });
    }

    // --- SELECTION MARKER ---
    if (!map.getSource("selection-point")) {
      map.addSource("selection-point", {
        type: "geojson",
        data: selectedPointRef.current
          ? {
              type: "FeatureCollection",
              features: [
                {
                  type: "Feature",
                  properties: {},
                  geometry: {
                    type: "Point",
                    coordinates: selectedPointRef.current,
                  },
                },
              ],
            }
          : { type: "FeatureCollection", features: [] },
      });
    }

    if (!map.getLayer("selection-point-layer")) {
      map.addLayer({
        id: "selection-point-layer",
        type: "circle",
        source: "selection-point",
        paint: {
          "circle-radius": 8,
          "circle-color": "#FF00FF",
          "circle-stroke-width": 2,
          "circle-stroke-color": "#000000",
          "circle-emissive-strength": 1, // Makes color visible in 3D night mode
        },
      });
    }
  };

  const addTerrain = (map: mapboxgl.Map) => {
    // Add terrain source if it doesn't exist
    if (!map.getSource("mapbox-dem")) {
      map.addSource("mapbox-dem", {
        type: "raster-dem",
        url: "mapbox://mapbox.mapbox-terrain-dem-v1",
        tileSize: 512,
        maxzoom: 14,
      });
    }
    // Enable terrain processing
    map.setTerrain({ source: "mapbox-dem", exaggeration: 1.5 });
  };

  useEffect(() => {
    // @ts-ignore
    mapboxgl.config.DISABLE_TELEMETRY = true;
    mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_API_KEY;

    if (!mapContainerRef.current) return;

    // Default to globe view if no center provided
    const initialCenter = center || ([-40, 20] as [number, number]);
    const initialZoom = center ? 12 : 1.5;

    const map = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: is3D ? STYLE_3D : isDarkMode ? STYLE_2D_DARK : STYLE_2D_LIGHT,
      center: initialCenter,
      zoom: initialZoom,
      pitch: is3D ? 60 : 0,
      minPitch: 0,
      maxPitch: 85,
      bearing: 0,
      projection: { name: "globe" },
      // Configure light preset for Standard style
      ...(is3D && {
        config: {
          basemap: {
            lightPreset: isDarkMode ? "night" : "day",
          },
        },
      }),
    });

    mapRef.current = map;

    map.on("style.load", () => {
      console.log("[MapboxHeatmap] Style loaded.");

      // Configure light preset for Standard style
      if (map.getStyle()?.name?.includes("Standard") || is3D) {
        try {
          map.setConfigProperty(
            "basemap",
            "lightPreset",
            isDarkMode ? "night" : "day"
          );
        } catch (e) {
          // Ignore if not Standard style
        }
      }

      map.setFog({
        range: [1.0, 10.0],
        color: "rgb(11, 11, 25)",
        "high-color": "rgb(36, 92, 223)",
        "space-color": "rgb(11, 11, 25)",
        "horizon-blend": 0.05,
        "star-intensity": 0.6,
      });

      // Add terrain to all styles (even 2D ones)
      addTerrain(map);

      addCustomLayers(map);
    });

    map.on("click", (e) => {
      const { lng, lat } = e.lngLat;
      console.log(
        `[MapboxHeatmap] Map clicked at Lat: ${lat.toFixed(
          6
        )}, Lng: ${lng.toFixed(6)}`
      );
      if (onMapClick) onMapClick(lat, lng);
    });

    // Create popup for hover tooltips
    const popup = new mapboxgl.Popup({
      closeButton: false,
      closeOnClick: false,
      className: "probability-popup",
    });
    popupRef.current = popup;

    // Add hover event for grid layer
    map.on("mousemove", "sar-grid-fill", (e) => {
      if (e.features && e.features.length > 0) {
        const feature = e.features[0];
        const probability = feature.properties?.probability;

        if (probability !== undefined && probability > 0.01) {
          map.getCanvas().style.cursor = "pointer";

          // Format probability as percentage
          const percentStr = (probability * 100).toFixed(1) + "%";

          popup
            .setLngLat(e.lngLat)
            .setHTML(
              `<div style="font-weight: 500; font-size: 13px;">Probability: <span style="color: #FF6B6B;">${percentStr}</span></div>`
            )
            .addTo(map);
        } else {
          popup.remove();
          map.getCanvas().style.cursor = "";
        }
      }
    });

    map.on("mouseleave", "sar-grid-fill", () => {
      map.getCanvas().style.cursor = "";
      popup.remove();
    });

    // Spin Globe Logic
    if (isSpinningRef.current) {
      let userInteracting = false;
      let frameId: number;

      const spinGlobe = () => {
        if (!isSpinningRef.current || userInteracting) {
          return;
        }

        const zoom = map.getZoom();
        if (zoom < 5) {
          const center = map.getCenter();
          // Decrease longitude to spin (approx 0.1 deg per frame for visible speed)
          center.lng -= 0.1;
          map.setCenter(center);
        }
        frameId = requestAnimationFrame(spinGlobe);
      };

      // Stop spinning on interaction
      const stopSpin = () => {
        userInteracting = true;
        isSpinningRef.current = false;
        if (frameId) cancelAnimationFrame(frameId);
      };

      map.on("mousedown", stopSpin);
      map.on("dragstart", stopSpin);
      map.on("touchstart", stopSpin);
      map.on("wheel", stopSpin);
      map.on("click", stopSpin);

      spinGlobe();
    }

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

  // Reactive 3D/2D and dark/light mode toggle
  useEffect(() => {
    if (!mapRef.current) return;
    const map = mapRef.current;

    const newStyle = is3D
      ? STYLE_3D
      : isDarkMode
      ? STYLE_2D_DARK
      : STYLE_2D_LIGHT;
    console.log(
      `[MapboxHeatmap] Switching to ${is3D ? "3D" : "2D"} ${
        isDarkMode ? "Dark" : "Light"
      } style`
    );

    // Set the new style
    map.setStyle(newStyle).once("style.load", () => {
      // Configure light preset for Standard style
      if (is3D) {
        try {
          map.setConfigProperty(
            "basemap",
            "lightPreset",
            isDarkMode ? "night" : "day"
          );
        } catch (e) {
          // Ignore if not Standard style
        }
      }

      // Add terrain to all styles
      addTerrain(map);

      // Re-add our custom layers after style change
      addCustomLayers(map);

      // Animate to appropriate pitch
      map.easeTo({
        pitch: is3D ? 60 : 0,
        duration: 500,
      });
    });
  }, [is3D, isDarkMode]);

  // Reactive Center Update
  useEffect(() => {
    if (!mapRef.current || !center) return;

    // Stop spinning if we fly to a new center
    isSpinningRef.current = false;

    console.log("[MapboxHeatmap] Flying to new center:", center);
    mapRef.current.flyTo({
      center: center,
      zoom: 12,
      pitch: is3D ? 60 : 0,
      essential: true,
    });
  }, [center]);

  return (
    <>
      <style>{`
        .probability-popup .mapboxgl-popup-content {
          background: rgba(26, 26, 26, 0.95);
          color: white;
          padding: 8px 12px;
          border-radius: 8px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
          border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .probability-popup .mapboxgl-popup-tip {
          border-top-color: rgba(26, 26, 26, 0.95);
        }
      `}</style>
      <div id="map" ref={mapContainerRef} style={{ height: "100%" }}></div>
    </>
  );
}
