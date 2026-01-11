//

import { Link } from "react-router-dom";

const Logo = ({ className = "w-7 h-7" }: { className?: string }) => {
  return (
    <Link
      to="/"
      className="flex items-center gap-2 hover:opacity-80 transition-opacity"
    >
      <img
        src="/images/logo.svg"
        alt="Waypoint Logo"
        className={`object-contain ${className}`}
      />
      <span className="text-xl font-bold tracking-tighter text-white">
        Waypoint
      </span>
    </Link>
  );
};

export default Logo;
