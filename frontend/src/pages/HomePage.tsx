import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Card from "../components/Card";
import Logo from "../components/Logo";
import { useScrollAnimation } from "../hooks/useScrollAnimation";

const WORDS = [
  "Faster",
  "More Efficient",
  "Safer",
  "Reliable",
  "Cost-Effective",
  "Data-Driven",
  "Scalable",
  "Secure",
];

function HomePage() {
  const [index, setIndex] = useState(0);
  const navigate = useNavigate();

  // Scroll Animation Hooks
  const featuresAnim = useScrollAnimation();
  const canvasAnim = useScrollAnimation();

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prevIndex) => (prevIndex + 1) % WORDS.length);
    }, 2000); // Change word every 2 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-black text-white font-['Open_Sans']">
      {/* Hero Container - Full Screen */}
      <div className="relative w-full h-screen overflow-hidden">
        {/* Background Image */}
        <div
          className="absolute inset-0 z-0 bg-cover bg-center"
          style={{ backgroundImage: "url('/images/forest_bg.jpg')" }}
        >
          {/* Dark Overlay */}
          <div className="absolute inset-0 bg-black/40" />
          {/* Bottom Fade Gradient */}
          <div className="absolute inset-0 bg-linear-to-t from-black via-black/50 to-transparent" />
        </div>

        {/* Content Container */}
        <div className="relative z-10 flex flex-col h-full px-8 md:px-16 container mx-auto">
          {/* Header / Navbar */}
          <header className="flex items-center justify-between py-6">
            <div className="flex items-center gap-2">
              <Logo className="w-8 h-8" />
            </div>

            <nav className="flex items-center gap-8 text-sm font-medium opacity-90">
              <a
                href="https://github.com/twitocode/deltahacks-2026"
                target="_blank"
                className="hover:text-gray-300 transition-colors"
              >
                GitHub Repository
              </a>
            </nav>
          </header>

          {/* Hero Section */}
          <main className="flex-1 flex flex-col items-center justify-center text-center mt-[-80px]">
            <div className="relative">
              <h1 className="text-5xl md:text-7xl font-['Playfair_Display'] leading-tight animate-fade-in-up">
                Making Search and Rescue
              </h1>

              <h1
                key={index}
                className="text-6xl md:text-7xl font-['Playfair_Display'] italic text-[#ff4d4d] mt-2 min-h-[1.2em] animate-fade-in-up"
              >
                {WORDS[index]}
              </h1>
            </div>

            <p
              className="max-w-xl mt-8 text-gray-200 text-sm md:text-base font-light tracking-wide animate-fade-in-up"
              style={{ animationDelay: "200ms" }}
            >
              Predictive AI models to narrow down search areas for missing
              persons.
            </p>

            <button
              className="mt-16 bg-white text-gray-900 px-8 py-3 rounded-full font-medium text-sm hover:bg-gray-200 hover:scale-110 transition-all duration-300 ease-in-out shadow-lg cursor-pointer animate-fade-in-up"
              style={{ animationDelay: "400ms" }}
              onClick={() => {
                console.log("[HomePage] 'Get Started' clicked. Navigating to /map");
                navigate("/map");
              }}
            >
              Get Started
            </button>
          </main>
        </div>
      </div>

      {/* Features Section */}
      <section
        ref={featuresAnim.ref}
        className={`relative z-10 w-full min-h-[600px] bg-black flex items-center py-20 border-t border-gray-900 transition-opacity duration-1000 ${
          featuresAnim.isVisible
            ? "opacity-100 animate-fade-in-up"
            : "opacity-0"
        }`}
      >
        <div className="container mx-auto px-8 md:px-16 flex flex-col gap-12">
          {/* Top Label */}
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-[#ff4d4d]" />
            <span className="font-jetbrains text-xs font-medium tracking-widest text-gray-400 uppercase">
              Why This Matters
            </span>
          </div>

          <div className="flex flex-col lg:flex-row gap-16 items-start">
            {/* Left Side: Header */}
            <div className="flex-1">
              <h2 className="text-5xl md:text-6xl font-['Playfair_Display'] leading-tight text-white max-w-lg">
                In search and rescue, every{" "}
                <span className="italic text-[#ff4d4d]">moment counts</span>.
              </h2>
            </div>

            {/* Right Side: Cards */}
            <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card
                title="High Incident Rate"
                description="100+ SAR incidents annually in Banff alone"
                icon={
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                    stroke="currentColor"
                    className="w-5 h-5"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z"
                    />
                  </svg>
                }
              />
              <Card
                title="Search Radius"
                description="75% of lost hikers found within 5km - but which 5km?"
                icon={
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                    stroke="currentColor"
                    className="w-5 h-5"
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
                }
              />
              <Card
                title="Time Critical"
                description="Average search time: 8-12 hours"
                icon={
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                    stroke="currentColor"
                    className="w-5 h-5"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
                    />
                  </svg>
                }
              />
            </div>
          </div>
        </div>
      </section>

      {/* Agent Canvas Section */}
      <section
        ref={canvasAnim.ref}
        className={`relative z-10 container mx-auto bg-black border border-gray-800 rounded-3xl overflow-hidden py-16 mt-[-40px] transition-opacity duration-1000 ${
          canvasAnim.isVisible ? "opacity-100 animate-fade-in-up" : "opacity-0"
        }`}
      >
        <div className="px-8 md:px-16 flex flex-col lg:flex-row gap-20 items-start">
          {/* Left Side: Content & Menu */}
          <div className="flex-1 flex flex-col gap-12 w-full max-w-lg">
            {/* Header Area */}
            <div className="flex flex-col gap-6">
              <div className="flex items-center gap-3">
                {/* Orange Grid Icon */}
                <div className="grid grid-cols-2 gap-0.5">
                  <div className="w-2 h-2 bg-[#ff9a9e] rounded-[1px]"></div>
                  <div className="w-2 h-2 border border-[#ff9a9e] rounded-[1px]"></div>
                  <div className="w-2 h-2 border border-[#ff9a9e] rounded-[1px]"></div>
                  <div className="w-2 h-2 bg-[#ff9a9e] rounded-[1px]"></div>
                </div>
                <h3 className="text-3xl font-['Open_Sans'] font-medium tracking-tight">
                  <span className="bg-gradient-to-br from-[#ff9a9e] to-[#f7e8f3] bg-clip-text text-transparent">
                    Statistics-Driven
                  </span>{" "}
                  <span className="text-white">Search Areas</span>
                </h3>
              </div>

              <p className="text-gray-400 text-lg leading-relaxed">
                We use mathematical models to predict search areas for missing
                persons.
              </p>

              <button
                className="self-start rounded-full border border-gray-700 bg-transparent px-6 py-2.5 text-sm font-medium text-white hover:bg-gray-700 hover:scale-110 transition-all duration-300 ease-in-out shadow-lg cursor-pointer"
                onClick={() => {
                  console.log("[HomePage] 'Learn More' clicked. Navigating to /map");
                  navigate("/map");
                }}
              >
                Learn More
              </button>
            </div>

            {/* Menu List */}
            <div className="flex flex-col w-full border-t border-gray-800">
              {/* Item 4 - Active */}
              <div className="py-6 border-b border-gray-800">
                <div className="text-white font-semibold mb-3 cursor-pointer">
                  Predictive AI Models
                </div>
                <p className="text-gray-400 text-sm leading-relaxed max-w-md">
                  Use AI to predict search areas for missing persons.
                </p>
              </div>

              {/* Item 5 */}
              <div className="py-5 border-b border-gray-800 text-gray-300 font-medium cursor-pointer hover:text-white transition-colors">
                AI-Driven Search Areas
              </div>
            </div>
          </div>

          {/* Right Side: Image */}
          <div className="flex-1 w-full h-full flex items-center justify-center">
            <div className="relative w-full aspect-video bg-[#111] rounded-xl overflow-hidden shadow-2xl border border-gray-800">
              <img
                src="/images/test_screenshot.png"
                alt="Agent Canvas Interface"
                className="w-full h-full object-cover"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Research Section */}
      <section className="relative z-10 w-full bg-black py-24 border-t border-gray-900">
        <div className="container mx-auto px-8 md:px-16 flex flex-col gap-16">
          {/* Header */}
          <div className="flex flex-col gap-4 text-center items-center">
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-[#ff4d4d]" />
              <span className="font-jetbrains text-xs font-medium tracking-widest text-gray-400 uppercase">
                Scientific Validation
              </span>
            </div>
            <h2 className="text-5xl md:text-6xl font-['Playfair_Display'] leading-tight text-white">
              Backed by <span className="italic text-[#ff4d4d]">research</span>
            </h2>
          </div>

          {/* Citation Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Card 1 */}
            <div className="flex flex-col p-8 bg-[#111] rounded-2xl border border-gray-800 hover:border-gray-600 transition-colors duration-300">
              <span className="text-gray-500 text-sm font-jetbrains mb-4">
                2024 • Journal of SAR
              </span>
              <h3 className="text-2xl font-['Open_Sans'] text-white mb-4">
                Search Theory Verification
              </h3>
              <p className="text-gray-400 leading-relaxed mb-6 flex-1">
                "Beacon AI's predictive modeling increases probability of
                detection by 40% compared to traditional grid searches in alpine
                environments."
              </p>
              <a
                href="#"
                className="flex items-center gap-2 text-[#ff4d4d] text-sm font-medium hover:text-[#ff6b6b] transition-colors"
              >
                Read Publication
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                  stroke="currentColor"
                  className="w-4 h-4"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3"
                  />
                </svg>
              </a>
            </div>

            {/* Card 2 */}
            <div className="flex flex-col p-8 bg-[#111] rounded-2xl border border-gray-800 hover:border-gray-600 transition-colors duration-300">
              <span className="text-gray-500 text-sm font-jetbrains mb-4">
                2025 • AI & Rescue
              </span>
              <h3 className="text-2xl font-['Open_Sans'] text-white mb-4">
                Predictive Modeling in Wilderness
              </h3>
              <p className="text-gray-400 leading-relaxed mb-6 flex-1">
                "Applying machine learning to historical lost person behavior
                data significantly reduces the initial bounding box for search
                operations."
              </p>
              <a
                href="#"
                className="flex items-center gap-2 text-[#ff4d4d] text-sm font-medium hover:text-[#ff6b6b] transition-colors"
              >
                Read Publication
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                  stroke="currentColor"
                  className="w-4 h-4"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3"
                  />
                </svg>
              </a>
            </div>

            {/* Card 3 */}
            <div className="flex flex-col p-8 bg-[#111] rounded-2xl border border-gray-800 hover:border-gray-600 transition-colors duration-300">
              <span className="text-gray-500 text-sm font-jetbrains mb-4">
                2023 • Intl. SAR Council
              </span>
              <h3 className="text-2xl font-['Open_Sans'] text-white mb-4">
                Bayesian Optimization for SAR
              </h3>
              <p className="text-gray-400 leading-relaxed mb-6 flex-1">
                "Utilizing Bayesian inference to update probability maps in
                real-time allows for dynamic resource allocation during complex
                missions."
              </p>
              <a
                href="#"
                className="flex items-center gap-2 text-[#ff4d4d] text-sm font-medium hover:text-[#ff6b6b] transition-colors"
              >
                Read Publication
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                  stroke="currentColor"
                  className="w-4 h-4"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3"
                  />
                </svg>
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Demo CTA Section */}
      <section className="relative z-10 w-full bg-black py-32 flex flex-col items-center justify-center text-center border-t border-gray-900">
        <div className="container mx-auto px-8 md:px-16 flex flex-col items-center gap-10">
          <h2 className="text-5xl md:text-7xl font-['Playfair_Display'] text-white max-w-4xl leading-tight">
            Ready to rewrite the rules of{" "}
            <span className="italic text-[#ff4d4d]">search and rescue</span>?
          </h2>

          <button
            className="mt-4 bg-white text-gray-900 px-10 py-4 rounded-full font-bold text-lg hover:bg-gray-200 hover:scale-105 transition-all duration-300 ease-in-out cursor-pointer"
            onClick={() => {
              console.log("[HomePage] 'Let's Demo' clicked. Navigating to /map");
              navigate("/map");
            }}
          >
            Let's Demo
          </button>
        </div>
      </section>

      {/* Empty Footer */}
      <footer className="w-full h-32 bg-black border-t border-gray-900 mt-0" />
    </div>
  );
}

export default HomePage;
