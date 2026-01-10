import { useState, useEffect } from 'react';

const WORDS = ["Faster", "More Efficient", "Safer", "Reliable",
  "Cost-Effective", "Data-Driven", "Scalable", "Secure",
];

function App() {
  const [index, setIndex] = useState(0);

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
              {/* Logo Icon (Lighthouse placeholder) */}
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-8 h-8">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 21a9.004 9.004 0 0 0 8.716-6.747M12 21a9.004 9.004 0 0 1-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 0 1 7.843 4.582M12 3a8.997 8.997 0 0 0-7.843 4.582m15.686 0A11.953 11.953 0 0 1 12 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0 1 21 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0 1 12 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 0 1 3 12c0-1.605.42-3.113 1.157-4.418" />
              </svg>
              <span className="text-xl font-semibold tracking-wide">Beacon.ai</span>
            </div>

            <nav className="flex items-center gap-8 text-sm font-medium opacity-90">
              <a href="#" className="hover:text-gray-300 transition-colors">About Us</a>
              <a href="#" className="hover:text-gray-300 transition-colors">Repository</a>
            </nav>
          </header>

          {/* Hero Section */}
          <main className="flex-1 flex flex-col items-center justify-center text-center mt-[-80px]">
            <div className="relative">
              <h1 className="text-5xl md:text-7xl font-['Playfair_Display'] leading-tight">
                Making Search and Rescue
              </h1>

              <h1
                key={index}
                className="text-6xl md:text-7xl font-['Playfair_Display'] italic text-[#ff4d4d] mt-2 min-h-[1.2em] animate-fade-in-up"
              >
                {WORDS[index]}
              </h1>
            </div>

            <p className="max-w-xl mt-8 text-gray-200 text-sm md:text-base font-light tracking-wide">
              Predictive AI models to narrow down search areas for missing persons.
            </p>

            <button className="mt-16 bg-white text-gray-900 px-8 py-3 rounded-full font-medium text-sm hover:bg-gray-300 hover:scale-110 transition-all duration-300 ease-in-out shadow-lg cursor-pointer">
              Get Started
            </button>
          </main>
        </div>

      </div>

      {/* Placeholder for the "black section" below */}
      <section className="relative z-10 w-full h-screen bg-black flex items-center justify-center">
        <p className="text-gray-500">More content...</p>
      </section>

    </div>
  );
}

export default App;
