import { useMutation } from "@tanstack/react-query";
import { useEffect, useMemo, useRef, useState } from "react";
import { fetchPrediction } from "../api";
import MapboxHeatmap from "../components/Heatmap";
import Logo from "../components/Logo";
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
}

function MapPage() {
  const [formData, setFormData] = useState<FormData>({
    latitude: "48.3562",
    longitude: "-120.6848",
    age: "",
    sex: "",
    experience: "",
  });
  const [timeOffset, setTimeOffset] = useState(0); // Hours from last seen (0, 1, 3...)
  const [isOnline, setIsOnline] = useState(true);

  // Raw Data from Server (or Fake Generator)
  const [serverData, setServerData] = useState<ServerGridResponse | null>(null);

  // Derived GeoJSON for the map (re-calculated when time or data changes)
  const heatmapGeoJson = useMemo(() => {
    if (!serverData) return undefined;
    // Map timeOffset to the nearest available key in predictions if needed
    // For now, we assume keys "0", "1", "3" etc. exist.
    // Simple fallback logic:
    const key = String(Math.abs(timeOffset));
    return convertServerGridToGeoJSON(serverData, key);
  }, [serverData, timeOffset]);

  // Center of the map to control view programmatically
  const [mapCenter, setMapCenter] = useState<[number, number] | undefined>(
    undefined
  );

  // Playback state
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1); // 0.5, 1, or 2
  const playbackIntervalRef = useRef<ReturnType<typeof setInterval> | null>(
    null
  );

  // Handle form input changes
  const handleInputChange = (field: keyof FormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  // Mutation for fetching prediction
  const { mutate: getPrediction, isPending } = useMutation({
    mutationFn: fetchPrediction,
    onSuccess: (data) => {
      console.log("Prediction received:", data);
      setServerData(data);
      setMapCenter([
        data.metadata.origin.longitude,
        data.metadata.origin.latitude,
      ]);
    },
    onError: (error) => {
      console.error("Error fetching prediction:", error);
      alert("Failed to fetch prediction data.");
    },
  });

  // Find person handler
  const handleFindPerson = () => {
    const lat = parseFloat(formData.latitude);
    const lng = parseFloat(formData.longitude);

    if (isNaN(lat) || isNaN(lng)) {
      alert("Please enter valid latitude and longitude coordinates.");
      return;
    }

    const skillMap: { [key: string]: number } = {
      novice: 1,
      intermediate: 3,
      experienced: 4,
      expert: 5,
    };

    const payload = {
      created_at: new Date().toISOString(),
      latitude: lat,
      longitude: lng,
      time_last_seen: new Date().toISOString(), // Use current time as start
      age: formData.age || "30",
      gender: formData.sex || "unknown",
      skill_level: skillMap[formData.experience] || 3,
    };

    getPrediction(payload);
  };

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
    if (isPlaying) {
      if (playbackIntervalRef.current) {
        clearInterval(playbackIntervalRef.current);
      }

      const intervalMs = 1000 / playbackSpeed;

      playbackIntervalRef.current = setInterval(() => {
        setTimeOffset((prev) => {
          if (prev >= 12) {
            setIsPlaying(false);
            return 12;
          }
          return prev + 1;
        });
      }, intervalMs);
    } else {
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
  }, [isPlaying, playbackSpeed]);

  // Playback controls
  const handlePlayPause = () => {
    if (!serverData) return;
    if (timeOffset >= 12 && !isPlaying) {
      setTimeOffset(0);
    }
    setIsPlaying(!isPlaying);
  };

  const handleSkipToStart = () => {
    setIsPlaying(false);
    setTimeOffset(0);
  };

  const handleSkipToEnd = () => {
    setIsPlaying(false);
    setTimeOffset(12);
  };

  const handleSpeedChange = (speed: number) => {
    setPlaybackSpeed(speed);
  };

  const formatTimeLabel = (hours: number) => {
    return `+${hours} hours`;
  };

  return (
    <div className="flex h-screen w-full bg-black font-['Open_Sans']">
      {/* Sidebar */}
      <div className="w-80 bg-[#1a1a1a] p-6 flex flex-col border-r border-gray-800 z-10">
        {/* Logo */}
        <div className="mb-12">
          <Logo className="w-8 h-8 rounded-lg" />
        </div>

        {/* Instructions */}
        <p className="text-gray-300 text-sm mb-6 leading-relaxed">
          Enter the last known location details
        </p>

        {/* Form Fields */}
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
                className="w-full bg-[#2a2a2a] border border-gray-700 rounded-md px-3 py-2 text-white text-sm focus:outline-none focus:border-gray-500 transition-colors"
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
                className="w-full bg-[#2a2a2a] border border-gray-700 rounded-md px-3 py-2 text-white text-sm focus:outline-none focus:border-gray-500 transition-colors"
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
                className="w-full bg-[#2a2a2a] border border-gray-700 rounded-md px-3 py-2 text-white text-sm focus:outline-none focus:border-gray-500 transition-colors"
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
                className="w-full bg-[#2a2a2a] border border-gray-700 rounded-md px-3 py-2 text-white text-sm focus:outline-none focus:border-gray-500 transition-colors appearance-none cursor-pointer"
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
        <div className="absolute top-4 right-4 z-50 bg-[#1a1a1a] px-4 py-2 rounded-full flex items-center gap-2 shadow-lg">
          <div
            className={`w-3 h-3 rounded-full ${
              isOnline ? "bg-green-500" : "bg-red-500"
            } animate-pulse`}
          />
          <span className="text-white text-sm font-medium">
            {isOnline ? "Online" : "Offline"}
          </span>
        </div>

        {/* MapboxHeatmap */}
        <div className="w-full h-full">
          <MapboxHeatmap
            data={heatmapGeoJson}
            center={mapCenter}
            onMapClick={(lat, lng) => {
              setFormData((prev) => ({
                ...prev,
                latitude: lat.toFixed(6),
                longitude: lng.toFixed(6),
              }));
            }}
          />
        </div>

        {/* Timeline Slider */}
        <div className="absolute bottom-0 left-0 right-0 bg-[#1a1a1a] py-4 px-8 z-50">
          <div className="flex items-center justify-center gap-4 mb-3">
            <div className="flex items-center gap-1">
              {[0.5, 1, 2].map((speed) => (
                <button
                  key={speed}
                  onClick={() => handleSpeedChange(speed)}
                  className={`px-2 py-1 text-xs rounded transition-colors ${
                    playbackSpeed === speed
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
                {Array.from({ length: 13 }, (_, i) => (
                  <div key={i} className="flex flex-col items-center">
                    <div
                      className={`w-0.5 ${
                        i % 3 === 0 ? "h-4" : "h-2"
                      } bg-gray-500`}
                    />
                  </div>
                ))}
              </div>
              <input
                type="range"
                min="0"
                max="12"
                value={timeOffset}
                onChange={(e) => setTimeOffset(parseInt(e.target.value))}
                className="absolute top-0 left-0 w-full h-full opacity-0 cursor-pointer z-10"
              />
              <div
                className="absolute top-1/2 transform -translate-y-1/2 -translate-x-1/2 pointer-events-none"
                style={{ left: `${(timeOffset / 12) * 100}%` }}
              >
                <div className="w-4 h-4 bg-white rounded-full border-2 border-gray-400 shadow-lg" />
              </div>
            </div>
            <div className="flex justify-between mt-2 text-xs text-gray-400 font-jetbrains">
              <span>+0h</span>
              <span>+3h</span>
              <span>+6h</span>
              <span>+9h</span>
              <span>+12h</span>
            </div>
            <div className="text-center mt-2">
              <span className="text-gray-300 text-xs font-jetbrains">
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
