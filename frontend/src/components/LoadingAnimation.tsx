import { useEffect, useState } from "react";

interface LoadingAnimationProps {
    isLoading: boolean;
}

export default function LoadingAnimation({ isLoading }: LoadingAnimationProps) {
    const [shouldRender, setShouldRender] = useState(isLoading);
    const [frameIndex, setFrameIndex] = useState(0);
    const [elapsedTime, setElapsedTime] = useState(0);

    // Keyframes based on the user's uploaded images description
    // 1. Corners (Indices: 0, 2, 6, 8)
    // 2. Cross / Edges (Indices: 1, 3, 5, 7)
    // 3. All Outer (Indices: 0, 1, 2, 3, 5, 6, 7, 8)
    // 4. None (Blink)
    const keyframes = [
        [0, 2, 6, 8],       // Frame 1: Corners
        [1, 3, 5, 7],       // Frame 2: Edges
        [0, 1, 2, 3, 5, 6, 7, 8], // Frame 3: All
        [],                 // Frame 4: None
    ];

    useEffect(() => {
        if (isLoading) {
            setShouldRender(true);
            setElapsedTime(0);

            // Animation Interval
            const animInterval = setInterval(() => {
                setFrameIndex((prev) => (prev + 1) % keyframes.length);
            }, 300);

            // Timer Interval
            const timerInterval = setInterval(() => {
                setElapsedTime(prev => prev + 0.1);
            }, 100);

            return () => {
                clearInterval(animInterval);
                clearInterval(timerInterval);
            };
        } else {
            const timer = setTimeout(() => setShouldRender(false), 500);
            return () => clearTimeout(timer);
        }
    }, [isLoading]);

    if (!shouldRender) return null;

    const currentActiveIndices = keyframes[frameIndex];

    // Determine message based on time
    let message = "Searching";
    if (elapsedTime > 30) message = "Truncating data points";
    else if (elapsedTime > 20) message = "Reconfiguring data";

    return (
        <div
            className={`absolute inset-0 z-50 flex items-center justify-center bg-black/30 transition-opacity duration-500 ${isLoading ? "opacity-100" : "opacity-0"
                }`}
        >
            <div className="flex flex-col items-center gap-8">
                {/* 3x3 Grid */}
                <div className="grid grid-cols-3 gap-3">
                    {Array.from({ length: 9 }).map((_, i) => {
                        // Number 4 is the center index
                        if (i === 4) {
                            return (
                                <div key={i} className="flex items-center justify-center w-12 h-12">
                                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M12 4V20M4 12H20" stroke="white" strokeWidth="2" strokeLinecap="round" />
                                    </svg>
                                </div>
                            );
                        }

                        const isActive = currentActiveIndices.includes(i);

                        return (
                            <div
                                key={i}
                                className={`w-12 h-12 rounded-lg border-2 border-white transition-all duration-300 ${isActive
                                    ? "bg-white shadow-[0_0_15px_rgba(255,255,255,0.8)] scale-105"
                                    : "bg-transparent scale-100"
                                    }`}
                            />
                        );
                    })}
                </div>

                <div className="flex flex-col items-center gap-2">
                    <div key={message} className="text-white font-jetbrains text-sm tracking-[0.2em] font-medium uppercase animate-[fadeIn_0.5s_ease-out]">
                        {message}
                    </div>
                    <div className="text-white/60 font-mono text-xs">
                        {elapsedTime.toFixed(1)}s
                    </div>
                </div>
            </div>
        </div>
    );
}
