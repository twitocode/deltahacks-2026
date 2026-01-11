//

import { Link } from 'react-router-dom';

const Logo = ({ className = "w-7 h-7" }: { className?: string }) => {
    return (
        <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <img
                src="/images/deltahacks_logo.png"
                alt="Beacon AI Logo"
                className={`object-contain ${className}`}
            />
            <span className="text-xl font-bold tracking-tighter text-white">Beacon.ai</span>
        </Link>
    );
};

export default Logo;
