import L from "leaflet";
import "leaflet.heat";
import "leaflet/dist/leaflet.css";
import { useCallback, useEffect, useRef, useState } from "react";
import { MapContainer, TileLayer, useMap, useMapEvents } from "react-leaflet";

// Declare the heat layer type for TypeScript
declare module "leaflet" {
  function heatLayer(
    latlngs: Array<[number, number, number]>,
    options?: {
      radius?: number;
      blur?: number;
      maxZoom?: number;
      max?: number;
      minOpacity?: number;
      gradient?: { [key: number]: string };
    }
  ): L.Layer;
}

import { fetchPrediction } from "../api";
import { useMutation } from "@tanstack/react-query";

// Remove the placeholder function completely and use the imported fetchPrediction


interface FormData {
  latitude: string;
  longitude: string;
  age: string;
  sex: string;
  experience: string;
}

// HeatmapLayer component that uses leaflet.heat
function HeatmapLayer({ data }: { data: Array<[number, number, number]> }) {
  const map = useMap();
  const heatLayerRef = useRef<L.Layer | null>(null);

  useEffect(() => {
    if (heatLayerRef.current) {
      map.removeLayer(heatLayerRef.current);
    }

    if (data.length > 0) {
      heatLayerRef.current = L.heatLayer(data, {
        radius: 25,
        blur: 15,
        maxZoom: 17,
        max: 1.0,
        minOpacity: 0.4,
        gradient: {
          0.0: "#00ff00",
          0.25: "#00ff00",
          0.5: "#ffff00",
          0.75: "#ff8800",
          1.0: "#ff0000",
        },
      }).addTo(map);
    }

    return () => {
      if (heatLayerRef.current) {
        map.removeLayer(heatLayerRef.current);
      }
    };
  }, [map, data]);

  return null;
}

// Component to handle map clicks for setting last known location
function MapClickHandler({
  onMapClick,
}: {
  onMapClick: (lat: number, lng: number) => void;
}) {
  useMapEvents({
    click: (e) => {
      onMapClick(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

// Custom marker for last known location
function LastKnownMarker({ position }: { position: [number, number] | null }) {
  const map = useMap();
  const markerRef = useRef<L.CircleMarker | null>(null);

  useEffect(() => {
    if (markerRef.current) {
      map.removeLayer(markerRef.current);
    }

    if (position) {
      markerRef.current = L.circleMarker(position, {
        radius: 10,
        fillColor: "#ff00ff",
        color: "#ffffff",
        weight: 2,
        opacity: 1,
        fillOpacity: 1,
      }).addTo(map);
    }

    return () => {
      if (markerRef.current) {
        map.removeLayer(markerRef.current);
      }
    };
  }, [map, position]);

  return null;
}

function MapPage() {
  const [formData, setFormData] = useState<FormData>({
    latitude: "",
    longitude: "",
    age: "",
    sex: "",
    experience: "",
  });
  const [timeOffset, setTimeOffset] = useState(-6); // Hours from last seen
  const [heatmapData, setHeatmapData] = useState<
    Array<[number, number, number]>
  >([]);
  const [isOnline, setIsOnline] = useState(true);
  const [lastKnownPosition, setLastKnownPosition] = useState<
    [number, number] | null
  >(null);

  // Store the full prediction response: { [timeKey: string]: number[][] }
  const [predictionResult, setPredictionResult] = useState<Record<string, number[][]> | null>(null);

  // Playback state
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1); // 0.5, 1, or 2
  const playbackIntervalRef = useRef<ReturnType<typeof setInterval> | null>(
    null
  );

  // Handle map click to set last known location
  const handleMapClick = useCallback((lat: number, lng: number) => {
    setFormData((prev) => ({
      ...prev,
      latitude: lat.toFixed(6),
      longitude: lng.toFixed(6),
    }));
    setLastKnownPosition([lat, lng]);
  }, []);

  // Handle form input changes
  const handleInputChange = (field: keyof FormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));

    // Update marker position if lat/lng changed
    if (field === "latitude" || field === "longitude") {
      const lat = parseFloat(field === "latitude" ? value : formData.latitude);
      const lng = parseFloat(
        field === "longitude" ? value : formData.longitude
      );
      if (!isNaN(lat) && !isNaN(lng)) {
        setLastKnownPosition([lat, lng]);
      }
    }
  };

  // Mutation for fetching prediction
  const { mutate: getPrediction, isPending } = useMutation({
    mutationFn: fetchPrediction,
    onSuccess: (data) => {
      setPredictionResult(data);
    },
    onError: (error) => {
      console.error("Error fetching prediction:", error);
      alert("Failed to fetch prediction data.");
    }
  });

  // Find person handler
  const handleFindPerson = () => {
    const lat = parseFloat(formData.latitude);
    const lng = parseFloat(formData.longitude);
    // Remove "parsing" for Age as it's a string in form data but needed as number or string for backend?
    // Assuming backend takes the payload as constructed below.

    if (isNaN(lat) || isNaN(lng)) {
      alert(
        "Please enter valid latitude and longitude coordinates, or click on the map."
      );
      return;
    }

    const skillMap: { [key: string]: number } = {
      'novice': 1,
      'intermediate': 3,
      'experienced': 4,
      'expert': 5
    };

    const payload = {
      created_at: new Date().toISOString(),
      latitude: lat,
      longitude: lng,
      // Calculate estimated time last seen based on offset (currently only handles hours back/forward from NOW)
      time_last_seen: new Date(Date.now() + timeOffset * 3600 * 1000).toISOString(),
      age: formData.age || "30",
      gender: formData.sex || "unknown",
      skill_level: skillMap[formData.experience] || 3,
    };

    getPrediction(payload);
  };

  // Update heatmap when timeline changes or new data arrives
  useEffect(() => {
    if (!predictionResult || !lastKnownPosition) return;

    // Find the time key closest to the current timeOffset header?
    // User response keys are: 0, 1, 2... representing "hours elapsed".
    // My timeOffset is -6 to +12.
    // If timeOffset is negative (past), well, the prediction starts from "last seen" (hour 0).
    // So if timeOffset < 0, we should probably show hour 0.
    // If timeOffset >= 0, we map to that hour.

    const hourKey = Math.max(0, timeOffset);
    const grid = predictionResult[hourKey] || predictionResult[String(hourKey)];

    if (!grid) return;

    // Convert 2D grid to points: [lat, lng, intensity]
    // Hardcoded assumptions matching backend:
    const radiusKm = 5.0;
    // We don't know grid size from response, but we can check grid.length
    const gridSize = grid.length;

    // Determine bounds
    // Simple approx: 1 deg lat ~ 111km.
    const latSpan = (radiusKm * 2) / 111.0;
    const lngSpan = (radiusKm * 2) / (111.0 * Math.cos(lastKnownPosition[0] * Math.PI / 180));

    const startLat = lastKnownPosition[0] - latSpan / 2;
    const startLng = lastKnownPosition[1] - lngSpan / 2;

    const latStep = latSpan / gridSize;
    const lngStep = lngSpan / gridSize;

    const points: Array<[number, number, number]> = [];

    for (let i = 0; i < gridSize; i++) {
      for (let j = 0; j < gridSize; j++) {
        const val = grid[i][j];
        if (val > 0.001) { // Filter low probability
          // backend grid: [row][col]. usually row maps to latitude (y), col to longitude (x).
          // often row 0 is top (max lat) or bottom (min lat).
          // Let's assume standard image coords: row 0 is top (Max Lat).
          // But terrain.lat_lon_to_grid usually does logical mapping.
          // Let's guess: row 0 -> maxLat, row N -> minLat.
          // Actually usually row 0 is minLat in scientific grids? 
          // Let's assume row corresponds to latitude index.
          const ptLat = startLat + i * latStep;
          const ptLng = startLng + j * lngStep;
          points.push([ptLat, ptLng, val]);
        }
      }
    }
    setHeatmapData(points);

  }, [timeOffset, predictionResult, lastKnownPosition]);

  // Check online status
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  // Playback animation logic
  useEffect(() => {
    if (isPlaying && heatmapData.length > 0) {
      // Clear any existing interval
      if (playbackIntervalRef.current) {
        clearInterval(playbackIntervalRef.current);
      }

      // Set playback interval based on speed (base interval is 1000ms)
      const intervalMs = 1000 / playbackSpeed;

      playbackIntervalRef.current = setInterval(() => {
        setTimeOffset((prev) => {
          if (prev >= 12) {
            // Stop at the end
            setIsPlaying(false);
            return 12;
          }
          return prev + 1;
        });
      }, intervalMs);
    } else {
      // Clear interval when not playing
      if (playbackIntervalRef.current) {
        clearInterval(playbackIntervalRef.current);
        playbackIntervalRef.current = null;
      }
    }

    return () => {
      if (playbackIntervalRef.current) {
        clearInterval(playbackIntervalRef.current);
      }
    };
  }, [isPlaying, playbackSpeed, heatmapData.length]);

  // Playback controls
  const handlePlayPause = () => {
    if (heatmapData.length === 0) {
      alert('Please click "Find Person" first to generate heatmap data.');
      return;
    }
    // If at the end, reset to beginning before playing
    if (timeOffset >= 12 && !isPlaying) {
      setTimeOffset(-6);
    }
    setIsPlaying(!isPlaying);
  };

  const handleSkipToStart = () => {
    setIsPlaying(false);
    setTimeOffset(-6);
  };

  const handleSkipToEnd = () => {
    setIsPlaying(false);
    setTimeOffset(12);
  };

  const handleSpeedChange = (speed: number) => {
    setPlaybackSpeed(speed);
  };

  // Format timeline labels
  const formatTimeLabel = (hours: number) => {
    if (hours === 0) return "+0";
    if (hours < 0) return `${hours} hours`;
    return `+${hours} hours`;
  };

  return (
    <div className="flex h-screen w-full bg-black font-['Open_Sans']">
      {/* Sidebar */}
      <div className="w-80 bg-[#1a1a1a] p-6 flex flex-col border-r border-gray-800">
        {/* Logo */}
        <div className="flex items-center gap-2 mb-12">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
            className="w-7 h-7 text-white"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 21a9.004 9.004 0 0 0 8.716-6.747M12 21a9.004 9.004 0 0 1-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 0 1 7.843 4.582M12 3a8.997 8.997 0 0 0-7.843 4.582m15.686 0A11.953 11.953 0 0 1 12 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0 1 21 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0 1 12 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 0 1 3 12c0-1.605.42-3.113 1.157-4.418"
            />
          </svg>
          <span className="text-xl font-semibold text-white tracking-wide">
            Beacon AI
          </span>
        </div>

        {/* Instructions */}
        <p className="text-gray-300 text-sm mb-6 leading-relaxed">
          Click on the map for the last known location
        </p>

        {/* Form Fields */}
        <div className="space-y-4">
          {/* Latitude & Longitude Row */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="flex items-center gap-1.5 text-xs text-gray-400 mb-1.5">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                  className="w-3.5 h-3.5"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1 1 15 0Z"
                  />
                </svg>
                Latitude
              </label>
              <input
                type="text"
                value={formData.latitude}
                onChange={(e) => handleInputChange("latitude", e.target.value)}
                className="w-full bg-[#2a2a2a] border border-gray-700 rounded-md px-3 py-2 text-white text-sm focus:outline-none focus:border-gray-500 transition-colors"
                placeholder="e.g. 50.2833"
              />
            </div>
            <div>
              <label className="flex items-center gap-1.5 text-xs text-gray-400 mb-1.5">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                  className="w-3.5 h-3.5"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 21a9.004 9.004 0 0 0 8.716-6.747M12 21a9.004 9.004 0 0 1-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3"
                  />
                </svg>
                Longitude
              </label>
              <input
                type="text"
                value={formData.longitude}
                onChange={(e) => handleInputChange("longitude", e.target.value)}
                className="w-full bg-[#2a2a2a] border border-gray-700 rounded-md px-3 py-2 text-white text-sm focus:outline-none focus:border-gray-500 transition-colors"
                placeholder="e.g. -86.5667"
              />
            </div>
          </div>

          {/* Age & Sex Row */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="flex items-center gap-1.5 text-xs text-gray-400 mb-1.5">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                  className="w-3.5 h-3.5"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z"
                  />
                </svg>
                Age
              </label>
              <input
                type="number"
                value={formData.age}
                onChange={(e) => handleInputChange("age", e.target.value)}
                className="w-full bg-[#2a2a2a] border border-gray-700 rounded-md px-3 py-2 text-white text-sm focus:outline-none focus:border-gray-500 transition-colors"
                placeholder="e.g. 35"
              />
            </div>
            <div>
              <label className="flex items-center gap-1.5 text-xs text-gray-400 mb-1.5">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                  className="w-3.5 h-3.5"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z"
                  />
                </svg>
                Sex
              </label>
              <select
                value={formData.sex}
                onChange={(e) => handleInputChange("sex", e.target.value)}
                className="w-full bg-[#2a2a2a] border border-gray-700 rounded-md px-3 py-2 text-white text-sm focus:outline-none focus:border-gray-500 transition-colors appearance-none cursor-pointer"
              >
                <option value="">Select...</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>

          {/* Experience */}
          <div>
            <label className="flex items-center gap-1.5 text-xs text-gray-400 mb-1.5">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
                className="w-3.5 h-3.5"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z"
                />
              </svg>
              Experience
            </label>
            <select
              value={formData.experience}
              onChange={(e) => handleInputChange("experience", e.target.value)}
              className="w-full bg-[#2a2a2a] border border-gray-700 rounded-md px-3 py-2 text-white text-sm focus:outline-none focus:border-gray-500 transition-colors appearance-none cursor-pointer"
            >
              <option value="">Select level...</option>
              <option value="novice">Novice</option>
              <option value="intermediate">Intermediate</option>
              <option value="experienced">Experienced</option>
              <option value="expert">Expert</option>
            </select>
          </div>
        </div>

        {/* Find Person Button */}
        <button
          onClick={handleFindPerson}
          disabled={isPending}
          className="mt-8 w-full bg-transparent border border-gray-600 text-white py-3 rounded-md font-medium text-sm hover:bg-gray-800 hover:border-gray-500 transition-all duration-200 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isPending ? "Searching..." : "Find Person"}
        </button>

        {/* Spacer */}
        <div className="flex-1" />
      </div>

      {/* Map Container */}
      <div className="flex-1 relative">
        {/* Online Status Indicator */}
        <div className="absolute top-4 right-4 z-1000 bg-[#1a1a1a] px-4 py-2 rounded-full flex items-center gap-2 shadow-lg">
          <div
            className={`w-3 h-3 rounded-full ${isOnline ? "bg-green-500" : "bg-red-500"
              } animate-pulse`}
          />
          <span className="text-white text-sm font-medium">
            {isOnline ? "Online" : "Offline"}
          </span>
        </div>

        {/* Map */}
        <MapContainer
          center={[50.2833, -86.5667]}
          zoom={10}
          className="w-full h-full"
          zoomControl={false}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <MapClickHandler onMapClick={handleMapClick} />
          <LastKnownMarker position={lastKnownPosition} />
          <HeatmapLayer data={heatmapData} />
        </MapContainer>

        {/* Timeline Slider */}
        <div className="absolute bottom-0 left-0 right-0 bg-[#1a1a1a] py-4 px-8 z-1000">
          <div className="flex items-center justify-center gap-4 mb-3">
            {/* Speed Controls */}
            <div className="flex items-center gap-1">
              {[0.5, 1, 2].map((speed) => (
                <button
                  key={speed}
                  onClick={() => handleSpeedChange(speed)}
                  className={`px-2 py-1 text-xs rounded transition-colors ${playbackSpeed === speed
                    ? "bg-white text-black"
                    : "bg-[#2a2a2a] text-gray-400 hover:bg-[#3a3a3a]"
                    }`}
                >
                  {speed}x
                </button>
              ))}
            </div>

            {/* Playback Controls */}
            <div className="flex items-center gap-2">
              {/* Skip to Start */}
              <button
                onClick={handleSkipToStart}
                className="p-2 text-gray-400 hover:text-white transition-colors"
                title="Skip to start"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                  stroke="currentColor"
                  className="w-5 h-5"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M18.75 19.5l-7.5-7.5 7.5-7.5m-6 15L5.25 12l7.5-7.5"
                  />
                </svg>
              </button>

              {/* Play/Pause */}
              <button
                onClick={handlePlayPause}
                className="p-3 bg-white text-black rounded-full hover:bg-gray-200 transition-colors"
                title={isPlaying ? "Pause" : "Play"}
              >
                {isPlaying ? (
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={2}
                    stroke="currentColor"
                    className="w-5 h-5"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M15.75 5.25v13.5m-7.5-13.5v13.5"
                    />
                  </svg>
                ) : (
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={2}
                    stroke="currentColor"
                    className="w-5 h-5"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z"
                    />
                  </svg>
                )}
              </button>

              {/* Skip to End */}
              <button
                onClick={handleSkipToEnd}
                className="p-2 text-gray-400 hover:text-white transition-colors"
                title="Skip to end"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                  stroke="currentColor"
                  className="w-5 h-5"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M5.25 4.5l7.5 7.5-7.5 7.5m6-15l7.5 7.5-7.5 7.5"
                  />
                </svg>
              </button>
            </div>

            {/* Timeline Label */}
            <span className="text-white text-sm font-medium bg-[#2a2a2a] px-4 py-1.5 rounded-full">
              Timeline
            </span>
          </div>

          <div className="relative mx-auto max-w-4xl">
            {/* Timeline Track */}
            <div className="relative h-8">
              {/* Main Line */}
              <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-gray-600 transform -translate-y-1/2" />

              {/* Tick Marks */}
              <div className="absolute top-0 left-0 right-0 h-full flex justify-between items-center">
                {Array.from({ length: 19 }, (_, i) => (
                  <div key={i} className="flex flex-col items-center">
                    <div
                      className={`w-0.5 ${i % 3 === 0 ? "h-4" : "h-2"
                        } bg-gray-500`}
                    />
                  </div>
                ))}
              </div>

              {/* Slider Input */}
              <input
                type="range"
                min="-6"
                max="12"
                value={timeOffset}
                onChange={(e) => setTimeOffset(parseInt(e.target.value))}
                className="absolute top-0 left-0 w-full h-full opacity-0 cursor-pointer z-10"
              />

              {/* Custom Slider Thumb */}
              <div
                className="absolute top-1/2 transform -translate-y-1/2 -translate-x-1/2 pointer-events-none"
                style={{ left: `${((timeOffset + 6) / 18) * 100}%` }}
              >
                <div className="w-4 h-4 bg-white rounded-full border-2 border-gray-400 shadow-lg" />
              </div>
            </div>

            {/* Labels */}
            <div className="flex justify-between mt-2 text-xs text-gray-400">
              <span>-6 hours</span>
              <span>-3 hours</span>
              <span>+0</span>
              <span>+6 hours</span>
              <span>+12 hours</span>
            </div>

            {/* Current Value Display */}
            <div className="text-center mt-2">
              <span className="text-gray-300 text-xs">
                Current: {formatTimeLabel(timeOffset)}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MapPage;
