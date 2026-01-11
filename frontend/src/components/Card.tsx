import { type ReactNode } from "react";

interface CardProps {
  title: string;
  description: string;
  icon: ReactNode;
}

const Card = ({ title, description, icon }: CardProps) => {
  return (
    <div className="flex flex-col gap-4 p-6 border-l border-gray-800 hover:bg-white/5 transition-colors duration-300">
      <div className="text-gray-400 mb-2">{icon}</div>
      <h3 className="text-lg font-medium text-white whitespace-nowrap">{title}</h3>
      <p className="text-gray-400 text-sm leading-relaxed">{description}</p>
    </div>
  );
};

export default Card;
