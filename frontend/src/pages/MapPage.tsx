import { useMutation } from "@tanstack/react-query";
import { useEffect, useMemo, useRef, useState } from "react";
import { fetchPrediction } from "../api";
import MapboxHeatmap from "../components/Heatmap";
import Logo from "../components/Logo";
import LoadingAnimation from "../components/LoadingAnimation";
import {
  convertServerGridToGeoJSON,
  type ServerGridResponse,
} from "../utils/heatmapGenerator";

interface FormData {
  latitude: string;
  longitude: string;
  age: string;
  sex: string;
  experience: string;
  timeLastSeen: string;
}

function MapPage() {
  const [formData, setFormData] = useState<FormData>({
    latitude: "48.3562",
    longitude: "-120.6848",
    age: "",
    sex: "",
    experience: "",
    timeLastSeen: new Date().toISOString().slice(0, 16),
  });
  const [timeOffset, setTimeOffset] = useState(0); // Minutes from last seen
  const [isOnline, setIsOnline] = useState(true);
  const [is3D, setIs3D] = useState(true); // 3D/2D view toggle
  const [isDarkMode, setIsDarkMode] = useState(true); // Light/Dark mode toggle

  // Raw Data from Server (or Fake Generator)
  const [serverData, setServerData] = useState<ServerGridResponse | null>(null);

  // Calculate dynamic max time from server data (keys are in MINUTES)
  const maxMinutes = useMemo(() => {
    if (!serverData) return 480; // Default to 8h if no data
    const keys = Object.keys(serverData.predictions).map(parseFloat);
    // Keys are already in minutes (0, 15, 30, ... 480)
    return Math.max(...keys, 0);
  }, [serverData]);

  // Derived GeoJSON for the map (re-calculated when time or data changes)
  const heatmapGeoJson = useMemo(() => {
    if (!serverData) return undefined;
    // timeOffset is already in minutes, pass directly
    return convertServerGridToGeoJSON(serverData, timeOffset);
  }, [serverData, timeOffset]);

  // Form validation - all fields required
  const isFormValid = useMemo(() => {
    const lat = parseFloat(formData.latitude);
    const lng = parseFloat(formData.longitude);
    return (
      !isNaN(lat) &&
      !isNaN(lng) &&
      lat >= -90 &&
      lat <= 90 &&
      lng >= -180 &&
      lng <= 180 &&
      formData.age.trim() !== "" &&
      !isNaN(parseInt(formData.age, 10)) &&
      formData.sex !== "" &&
      formData.experience !== "" &&
      formData.timeLastSeen !== ""
    );
  }, [formData]);

  // Track which fields have errors (for showing red borders)
  const [showErrors, setShowErrors] = useState(false);

  const fieldErrors = useMemo(() => {
    const lat = parseFloat(formData.latitude);
    const lng = parseFloat(formData.longitude);
    return {
      latitude: isNaN(lat) || lat < -90 || lat > 90,
      longitude: isNaN(lng) || lng < -180 || lng > 180,
      age: formData.age.trim() === "" || isNaN(parseInt(formData.age, 10)),
      sex: formData.sex === "",
      experience: formData.experience === "",
      timeLastSeen: formData.timeLastSeen === "",
    };
  }, [formData]);

  // Center of the map
  const [mapCenter, setMapCenter] = useState<[number, number] | undefined>(
    undefined
  );

  // Playback state
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const playbackIntervalRef = useRef<ReturnType<typeof setInterval> | null>(
    null
  );

  const handleInputChange = (field: keyof FormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  // Update map center when lat/lng input fields change
  useEffect(() => {
    const lat = parseFloat(formData.latitude);
    const lng = parseFloat(formData.longitude);

    if (
      !isNaN(lat) &&
      !isNaN(lng) &&
      lat >= -90 &&
      lat <= 90 &&
      lng >= -180 &&
      lng <= 180
    ) {
      setMapCenter([lng, lat]);
    }
  }, [formData.latitude, formData.longitude]);

  // Mutation for fetching prediction (Simulates API or Fake Data)
  const { mutate: getPrediction, isPending } = useMutation({
    mutationFn: fetchPrediction,
    onSuccess: (data) => {
      console.log(
        "[MapPage] Prediction received successfully. Metadata:",
        data.metadata
      );
      setServerData(data);
      setTimeOffset(0); // Reset timeline to start
      setIsPlaying(false); // Stop any playback
      setMapCenter([
        data.metadata.origin.longitude,
        data.metadata.origin.latitude,
      ]);
    },
    onError: (error) => {
      console.error("[MapPage] Error fetching prediction:", error);
      alert("Failed to fetch prediction data.");
    },
  });

  const handleFindPerson = () => {
    console.log(
      "[MapPage] handleFindPerson initiated with form data:",
      formData
    );

    // Show errors if form is invalid
    if (!isFormValid) {
      setShowErrors(true);
      return;
    }

    // Clear errors on successful validation
    setShowErrors(false);

    const lat = parseFloat(formData.latitude);
    const lng = parseFloat(formData.longitude);

    const payload = {
      latitude: lat,
      longitude: lng,
      time_last_seen: new Date(formData.timeLastSeen).toISOString(),
      age: formData.age ? parseInt(formData.age, 10) : 35,
      sex: formData.sex || "unknown",
      experience: formData.experience || "novice",
    };

    console.log(
      "[MapPage] Dispatching prediction request with payload:",
      payload
    );
    getPrediction(payload);
  };

  useEffect(() => {
    const handleOnline = () => {
      console.log("[MapPage] Network status: Online");
      setIsOnline(true);
    };
    const handleOffline = () => {
      console.warn("[MapPage] Network status: Offline");
      setIsOnline(false);
    };
    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);
    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  useEffect(() => {
    if (isPlaying) {
      if (playbackIntervalRef.current)
        clearInterval(playbackIntervalRef.current);
      const intervalMs = 1000 / playbackSpeed;
      console.log(
        `[MapPage] Starting playback. Speed: ${playbackSpeed}x, Interval: ${intervalMs}ms`
      );

      playbackIntervalRef.current = setInterval(() => {
        setTimeOffset((prev) => {
          if (prev >= maxMinutes) {
            console.log(
              `[MapPage] Playback reached end (${maxMinutes}m). Stopping.`
            );
            setIsPlaying(false);
            return maxMinutes;
          }
          return prev + 15;
        });
      }, intervalMs);
    } else {
      if (playbackIntervalRef.current) {
        console.log("[MapPage] Pausing playback.");
        clearInterval(playbackIntervalRef.current);
        playbackIntervalRef.current = null;
      }
    }
    return () => {
      if (playbackIntervalRef.current)
        clearInterval(playbackIntervalRef.current);
    };
  }, [isPlaying, playbackSpeed, maxMinutes]);

  const handlePlayPause = () => {
    if (!serverData) {
      console.warn("[MapPage] Play clicked but no data loaded.");
      alert("Please click 'Find Person' first.");
      return;
    }
    if (timeOffset >= maxMinutes && !isPlaying) {
      console.log("[MapPage] Restarting playback from 0.");
      setTimeOffset(0);
    }
    setIsPlaying(!isPlaying);
  };

  const handleSkipToStart = () => {
    console.log("[MapPage] Skipping to start.");
    setIsPlaying(false);
    setTimeOffset(0);
  };

  const handleSkipToEnd = () => {
    console.log("[MapPage] Skipping to end.");
    setIsPlaying(false);
    setTimeOffset(maxMinutes);
  };

  const handleSpeedChange = (speed: number) => {
    console.log(`[MapPage] Changing playback speed to ${speed}x`);
    setPlaybackSpeed(speed);
  };
  const formatTimeLabel = (minutes: number) => {
    const hrs = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hrs === 0) return `+${mins}m`;
    if (mins === 0) return `+${hrs}h`;
    return `+${hrs}h ${mins}m`;
  };

  return (
    <div className="flex h-screen w-full bg-black font-['Open_Sans']">
      {/* Sidebar */}
      <div className="w-80 bg-[#1a1a1a] p-6 flex flex-col border-r border-gray-800 z-10">
        <div className="mb-12">
          <Logo className="w-8 h-8 rounded-lg" />
        </div>
        <p className="text-gray-300 text-sm mb-6 leading-relaxed">
          Enter the last known location details
        </p>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="flex items-center gap-1.5 text-xs text-gray-400 mb-1.5 font-jetbrains">
                Latitude
              </label>
              <input
                type="text"
                value={formData.latitude}
                onChange={(e) => handleInputChange("latitude", e.target.value)}
                className={`w-full bg-[#2a2a2a] border rounded-md px-3 py-2 text-white text-sm focus:outline-none transition-colors ${
                  showErrors && fieldErrors.latitude
                    ? "border-red-500"
                    : "border-gray-700 focus:border-gray-500"
                }`}
              />
            </div>
            <div>
              <label className="flex items-center gap-1.5 text-xs text-gray-400 mb-1.5 font-jetbrains">
                Longitude
              </label>
              <input
                type="text"
                value={formData.longitude}
                onChange={(e) => handleInputChange("longitude", e.target.value)}
                className={`w-full bg-[#2a2a2a] border rounded-md px-3 py-2 text-white text-sm focus:outline-none transition-colors ${
                  showErrors && fieldErrors.longitude
                    ? "border-red-500"
                    : "border-gray-700 focus:border-gray-500"
                }`}
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="flex items-center gap-1.5 text-xs text-gray-400 mb-1.5 font-jetbrains">
                Age
              </label>
              <input
                type="number"
                value={formData.age}
                onChange={(e) => handleInputChange("age", e.target.value)}
                className={`w-full bg-[#2a2a2a] border rounded-md px-3 py-2 text-white text-sm focus:outline-none transition-colors ${
                  showErrors && fieldErrors.age
                    ? "border-red-500"
                    : "border-gray-700 focus:border-gray-500"
                }`}
                placeholder="e.g. 35"
              />
            </div>
            <div>
              <label className="flex items-center gap-1.5 text-xs text-gray-400 mb-1.5 font-jetbrains">
                Sex
              </label>
              <select
                value={formData.sex}
                onChange={(e) => handleInputChange("sex", e.target.value)}
                className={`w-full bg-[#2a2a2a] border rounded-md px-3 py-2 text-white text-sm focus:outline-none transition-colors appearance-none cursor-pointer ${
                  showErrors && fieldErrors.sex
                    ? "border-red-500"
                    : "border-gray-700 focus:border-gray-500"
                }`}
              >
                <option value="">Select...</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>
          <div>
            <label className="flex items-center gap-1.5 text-xs text-gray-400 mb-1.5 font-jetbrains">
              Experience
            </label>
            <select
              value={formData.experience}
              onChange={(e) => handleInputChange("experience", e.target.value)}
              className={`w-full bg-[#2a2a2a] border rounded-md px-3 py-2 text-white text-sm focus:outline-none transition-colors appearance-none cursor-pointer ${
                showErrors && fieldErrors.experience
                  ? "border-red-500"
                  : "border-gray-700 focus:border-gray-500"
              }`}
            >
              <option value="">Select level...</option>
              <option value="novice">Novice</option>
              <option value="intermediate">Intermediate</option>
              <option value="experienced">Experienced</option>
              <option value="expert">Expert</option>
            </select>
          </div>
          <div>
            <label className="flex items-center gap-1.5 text-xs text-gray-400 mb-1.5 font-jetbrains">
              Time Last Seen
            </label>
            <input
              type="datetime-local"
              value={formData.timeLastSeen}
              onChange={(e) =>
                handleInputChange("timeLastSeen", e.target.value)
              }
              className={`w-full bg-[#2a2a2a] border rounded-md px-3 py-2 text-white text-sm focus:outline-none transition-colors ${
                showErrors && fieldErrors.timeLastSeen
                  ? "border-red-500"
                  : "border-gray-700 focus:border-gray-500"
              }`}
            />
          </div>
        </div>
        <button
          onClick={handleFindPerson}
          disabled={isPending}
          className="mt-8 w-full bg-transparent border border-gray-600 text-white py-3 rounded-md font-medium text-sm hover:bg-gray-700 hover:border-gray-500 transition-all duration-200 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isPending ? "Searching..." : "Find Person"}
        </button>
        <div className="flex-1" />
      </div>

      {/* Map Container */}
      <div className="flex-1 relative">
        <div className="absolute top-4 right-4 z-50 flex items-center gap-3">
          {/* 2D/3D Toggle Button */}
          <button
            onClick={() => setIs3D(!is3D)}
            className="bg-[#1a1a1a] px-4 py-2 rounded-full flex items-center gap-2 shadow-lg hover:bg-[#2a2a2a] transition-colors cursor-pointer"
            title={is3D ? "Switch to 2D" : "Switch to 3D"}
          >
            {is3D ? (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
                className="w-5 h-5 text-white"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="m21 7.5-9-5.25L3 7.5m18 0-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9"
                />
              </svg>
            ) : (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
                className="w-5 h-5 text-white"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M5.25 7.5A2.25 2.25 0 0 1 7.5 5.25h9a2.25 2.25 0 0 1 2.25 2.25v9a2.25 2.25 0 0 1-2.25 2.25h-9a2.25 2.25 0 0 1-2.25-2.25v-9Z"
                />
              </svg>
            )}
            <span className="text-white text-sm font-medium">
              {is3D ? "3D" : "2D"}
            </span>
          </button>
          {/* Light/Dark Mode Toggle */}
          <button
            onClick={() => setIsDarkMode(!isDarkMode)}
            className="bg-[#1a1a1a] px-4 py-2 rounded-full flex items-center gap-2 shadow-lg hover:bg-[#2a2a2a] transition-colors cursor-pointer"
            title={isDarkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
          >
            {isDarkMode ? (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
                className="w-5 h-5 text-white"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M21.752 15.002A9.72 9.72 0 0 1 18 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 0 0 3 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 0 0 9.002-5.998Z"
                />
              </svg>
            ) : (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
                className="w-5 h-5 text-yellow-400"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M12 3v2.25m6.364.386-1.591 1.591M21 12h-2.25m-.386 6.364-1.591-1.591M12 18.75V21m-4.773-4.227-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0Z"
                />
              </svg>
            )}
          </button>
          {/* Online Status */}
          <div className="bg-[#1a1a1a] px-4 py-2 rounded-full flex items-center gap-2 shadow-lg">
            <div
              className={`w-3 h-3 rounded-full ${isOnline ? "bg-green-500" : "bg-red-500"
                } animate-pulse`}
            />
            <span className="text-white text-sm font-medium">
              {isOnline ? "Online" : "Offline"}
            </span>
          </div>
        </div>


        {/* Loading Overlay */}
        <LoadingAnimation isLoading={isPending} />

        <div className="w-full h-full">
          <MapboxHeatmap
            data={heatmapGeoJson}
            center={mapCenter}
            is3D={is3D}
            isDarkMode={isDarkMode}
            selectedPoint={
              !isNaN(parseFloat(formData.latitude)) &&
                !isNaN(parseFloat(formData.longitude))
                ? [
                  parseFloat(formData.longitude),
                  parseFloat(formData.latitude),
                ]
                : null
            }
            onMapClick={(lat, lng) => {
              setFormData((prev) => ({
                ...prev,
                latitude: lat.toFixed(6),
                longitude: lng.toFixed(6),
              }));
            }}
          />
        </div>
        <div className="absolute bottom-0 left-0 right-0 bg-[#1a1a1a] py-4 px-8 z-50">
          <div className="flex items-center justify-center gap-4 mb-3">
            <div className="flex items-center gap-1">
              {[0.5, 1, 2, 10, 20, 50].map((speed) => (
                <button
                  key={speed}
                  onClick={() => handleSpeedChange(speed)}
                  className={`px-2 py-1 text-xs rounded transition-colors ${playbackSpeed === speed
                    ? "bg-white text-black"
                    : "bg-[#2a2a2a] text-gray-400 hover:bg-gray-700"
                    }`}
                >
                  {speed}x
                </button>
              ))}
            </div>
            <div className="flex items-center gap-2">
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
              <button
                onClick={handlePlayPause}
                className="p-3 bg-white text-black rounded-full hover:bg-gray-100 transition-colors"
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
            <span className="text-white text-sm font-medium bg-[#2a2a2a] px-4 py-1.5 rounded-full font-jetbrains">
              Timeline
            </span>
          </div>
          <div className="relative mx-auto max-w-4xl">
            <div className="relative h-8">
              <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-gray-600 transform -translate-y-1/2" />
              <div className="absolute top-0 left-0 right-0 h-full flex justify-between items-center">
                {Array.from(
                  { length: Math.floor(maxMinutes / 60) + 1 },
                  (_, i) => (
                    <div key={i} className="flex flex-col items-center">
                      <div
                        className={`w-0.5 ${i % 3 === 0 ? "h-4" : "h-2"
                          } bg-gray-500`}
                      />
                    </div>
                  )
                )}
              </div>
              <input
                type="range"
                min="0"
                max={maxMinutes}
                step="15"
                value={timeOffset}
                onChange={(e) => setTimeOffset(parseInt(e.target.value))}
                className="absolute top-0 left-0 w-full h-full opacity-0 cursor-pointer z-10"
              />
              <div
                className="absolute top-1/2 transform -translate-y-1/2 -translate-x-1/2 pointer-events-none"
                style={{ left: `${(timeOffset / maxMinutes) * 100}%` }}
              >
                <div className="w-4 h-4 bg-white rounded-full border-2 border-gray-400 shadow-lg" />
              </div>
            </div>
            <div className="flex justify-between mt-2 text-xs text-gray-400 font-jetbrains">
              {/* Show labels every 2 hours for better accuracy */}
              {Array.from(
                { length: Math.floor(maxMinutes / 120) + 1 },
                (_, i) => (
                  <span key={i}>+{i * 2}h</span>
                )
              )}
            </div>
            <div className="text-center mt-2">
              <span className="text-gray-300 text-xs font-jetbrains">
                Current: {formatTimeLabel(timeOffset)}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div >
  );
}

export default MapPage;
